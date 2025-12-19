from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, Union

import httpx

from .errors import BabyAPIError
from .resources import BabyResource, ChatResource, CompletionsResource
from .streaming import SSEEvent, _iter_sse_text, parse_sse_events

DEFAULT_BASE_URL = "https://api.babyapi.org"
DEFAULT_TIMEOUT_S = 60.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BASE_DELAY_S = 0.25

# Matches your JS SDK aliases (snake_case and camelCase inputs)
BABY_OPTION_KEY_ALIASES = {
    "max_tokens": "max_tokens",
    "maxTokens": "max_tokens",
    "temperature": "temperature",
    "top_p": "top_p",
    "topP": "top_p",
    "top_k": "top_k",
    "topK": "top_k",
    "stop": "stop",
    "presence_penalty": "presence_penalty",
    "presencePenalty": "presence_penalty",
    "frequency_penalty": "frequency_penalty",
    "frequencyPenalty": "frequency_penalty",
}

NON_RETRYABLE_ERROR_CODES = {
    "USER_INPUT",
    "INVALID_REQUEST_PAYLOAD",
    "INVALID_PROMPT",
    "MODEL_REQUIRED",
}

BabyInferInput = Union[str, Mapping[str, Any]]


@dataclass
class RequestOptions:
    api_key: Optional[str] = None
    timeout_s: Optional[float] = None
    max_retries: Optional[int] = None
    headers: Optional[Mapping[str, str]] = None


def _coerce_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered in ("1", "true", "yes", "on")
    return False


def _normalize_headers(headers: Optional[Mapping[str, str]]) -> Dict[str, str]:
    if headers is None:
        return {}
    if not isinstance(headers, Mapping):
        raise BabyAPIError("headers must be a mapping", code="INVALID_HEADERS")
    out: Dict[str, str] = {}
    for k, v in headers.items():
        if v is None:
            continue
        out[str(k)] = str(v)
    return out


def _extract_error_code(details: Optional[Mapping[str, Any]]) -> Optional[str]:
    if not isinstance(details, Mapping):
        return None
    error_block = details.get("error")
    if isinstance(error_block, Mapping):
        maybe = error_block.get("code") or error_block.get("error")
        return maybe if isinstance(maybe, str) else None
    if isinstance(error_block, str):
        return error_block
    direct = details.get("code")
    return direct if isinstance(direct, str) else None


def _parse_retry_after_seconds(headers: Mapping[str, Any]) -> Optional[float]:
    value = headers.get("retry-after") or headers.get("Retry-After")
    if value is None:
        return None

    # seconds
    try:
        seconds = float(value)
        if seconds >= 0:
            return seconds
    except (TypeError, ValueError):
        pass

    # HTTP-date
    try:
        dt = parsedate_to_datetime(str(value))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = (dt - datetime.now(timezone.utc)).total_seconds()
        if delta > 0:
            return delta
    except Exception:
        return None

    return None


def _with_jitter(seconds: float) -> float:
    if seconds <= 0:
        return 0.0
    factor = 0.8 + random.random() * 0.4
    return max(0.0, seconds * factor)


def _pick_baby_option_fields(source: Mapping[str, Any]) -> Dict[str, Any]:
    picked: Dict[str, Any] = {}
    for key in BABY_OPTION_KEY_ALIASES:
        if key in source:
            v = source[key]
            if v is not None:
                picked[key] = v
    return picked


def _normalize_baby_options(options: Mapping[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for key, value in options.items():
        mapped = BABY_OPTION_KEY_ALIASES.get(key)
        if not mapped:
            continue
        if value is None:
            continue
        normalized[mapped] = value
    return normalized


def _default_should_retry(
    status: Optional[int],
    err: Optional[BaseException],
    details: Optional[Mapping[str, Any]],
) -> bool:
    # network/timeout errors: retry (status None + err present)
    if err is not None and status is None:
        return True
    if status is None:
        return False
    if status >= 500:
        return True
    if status == 429:
        return True
    if status in (400, 422):
        return False
    code = _extract_error_code(details)
    if code and code in NON_RETRYABLE_ERROR_CODES:
        return False
    return status == 408


class BabyAPI:
    """
    BabyAPI Python Client.

    OpenAI-compatible endpoints:
      - POST /v1/completions
      - POST /v1/chat/completions

    Streaming uses SSE (stream=True), yielding SSEEvent.
    BabyAPI convenience endpoint:
      - POST /infer (simple text-in, text-out) via client.baby.infer(...)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_base_delay_s: float = DEFAULT_RETRY_BASE_DELAY_S,
        default_headers: Optional[Mapping[str, str]] = None,
        default_model: Optional[str] = None,
        should_retry: Optional[
            Callable[[Optional[int], Optional[BaseException], Optional[Mapping[str, Any]]], bool]
        ] = None,
    ):
        self.api_key = api_key or os.getenv("BABYAPI_API_KEY") or os.getenv("BABY_API_KEY")
        self.base_url = (base_url or os.getenv("BABYAPI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")

        config_default_model = (default_model or "").strip()
        env_default_model = (os.getenv("BABYAPI_DEFAULT_MODEL") or "").strip()
        self.default_model = config_default_model or env_default_model or None

        self.timeout_s = float(timeout_s)
        self.max_retries = max(0, int(max_retries))
        self.retry_base_delay_s = max(0.0, float(retry_base_delay_s))

        self.default_headers = _normalize_headers(default_headers)
        self._should_retry_cb = should_retry

        self.completions = CompletionsResource(self)
        self.chat = ChatResource(self)
        self.baby = BabyResource(self)

        # client-level timeout None; we pass per-request timeouts explicitly
        self._client = httpx.Client(base_url=self.base_url, timeout=None)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BabyAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False

    # -------- Public convenience --------

    def infer(
        self,
        body: Optional[Mapping[str, Any]] = None,
        *,
        request_options: Optional[Union[RequestOptions, Mapping[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        JS-parity convenience:
          - if merged has messages => /v1/chat/completions
          - else if merged has prompt => /v1/completions

        Supports:
          client.infer({"model": "...", "prompt": "..."})
          client.infer(model="...", prompt="...")
        """
        merged: Dict[str, Any] = {}
        if body is not None:
            if not isinstance(body, Mapping):
                raise BabyAPIError("infer() body must be a mapping", code="INVALID_INFER_INPUT")
            merged.update(dict(body))
        merged.update(kwargs)

        if "messages" in merged:
            return self.chat.completions.create(request_options=request_options, **merged)
        if "prompt" in merged:
            return self.completions.create(request_options=request_options, **merged)

        raise BabyAPIError(
            "infer() requires either `messages` (chat) or `prompt` (completions)",
            code="INVALID_INFER_INPUT",
        )

    # -------- Internal helpers --------

    def _normalize_request_options(
        self,
        options: Optional[Union[RequestOptions, Mapping[str, Any]]],
    ) -> RequestOptions:
        if options is None:
            return RequestOptions()
        if isinstance(options, RequestOptions):
            return options
        if isinstance(options, Mapping):
            return RequestOptions(
                api_key=options.get("api_key"),
                timeout_s=options.get("timeout_s"),
                max_retries=options.get("max_retries"),
                headers=options.get("headers"),
            )
        raise BabyAPIError("request_options must be a mapping or RequestOptions", code="INVALID_REQUEST_OPTIONS")

    def _build_headers(
        self,
        api_key: str,
        per_request_headers: Optional[Mapping[str, str]] = None,
        extra: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, str]:
        headers = dict(self.default_headers)
        headers.update(_normalize_headers(per_request_headers))
        headers["Authorization"] = f"Bearer {api_key}"
        if extra:
            for k, v in extra.items():
                if v is None:
                    continue
                headers[str(k)] = str(v)
        return headers

    def _resolve_timeout(self, override: Optional[float]) -> float:
        if override is None:
            return self.timeout_s
        try:
            value = float(override)
        except (TypeError, ValueError):
            raise BabyAPIError("timeout_s must be numeric", code="INVALID_TIMEOUT")
        if value <= 0:
            raise BabyAPIError("timeout_s must be > 0", code="INVALID_TIMEOUT")
        return value

    def _resolve_max_retries(self, override: Optional[int]) -> int:
        if override is None:
            return self.max_retries
        try:
            value = int(override)
        except (TypeError, ValueError):
            raise BabyAPIError("max_retries must be an integer", code="INVALID_MAX_RETRIES")
        if value < 0:
            raise BabyAPIError("max_retries must be >= 0", code="INVALID_MAX_RETRIES")
        return value

    def _next_retry_delay(self, attempt: int, retry_after_s: Optional[float]) -> float:
        base = retry_after_s if retry_after_s is not None else self.retry_base_delay_s * (2 ** attempt)
        return _with_jitter(base)

    def _wrap_network_error(self, exc: Exception) -> BabyAPIError:
        message = str(exc) or "Network error"
        code = "TIMEOUT" if isinstance(exc, httpx.TimeoutException) else None
        return BabyAPIError(message=message, code=code, cause=exc)

    def _should_retry(
        self,
        status: Optional[int],
        err: Optional[BaseException],
        details: Optional[Mapping[str, Any]],
    ) -> bool:
        if self._should_retry_cb:
            try:
                return bool(self._should_retry_cb(status, err, details))
            except Exception:
                return _default_should_retry(status, err, details)
        return _default_should_retry(status, err, details)

    def _post_json(
        self,
        path: str,
        body: Mapping[str, Any],
        *,
        request_options: Optional[Union[RequestOptions, Mapping[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(body, Mapping):
            raise BabyAPIError("Request body must be a JSON object", code="INVALID_REQUEST_BODY")

        # OpenAI-style: stream flag exists, but in this SDK streaming is via .stream()
        if _coerce_boolean(body.get("stream")):
            raise BabyAPIError(
                "For streaming, use .stream(...) or set stream=False for .create(...)",
                code="STREAM_METHOD_REQUIRED",
            )

        opts = self._normalize_request_options(request_options)
        api_key = opts.api_key or self.api_key
        if not api_key:
            raise BabyAPIError("API key is required (set BABYAPI_API_KEY or pass api_key)", code="API_KEY_REQUIRED")

        timeout = self._resolve_timeout(opts.timeout_s)
        max_retries = self._resolve_max_retries(opts.max_retries)
        headers = self._build_headers(api_key, opts.headers)

        attempt = 0
        last_error: Optional[BabyAPIError] = None

        while attempt <= max_retries:
            try:
                resp = self._client.post(path, json=dict(body), headers=headers, timeout=timeout)
            except httpx.RequestError as exc:
                wrapped = self._wrap_network_error(exc)
                last_error = wrapped
                if attempt < max_retries and self._should_retry(None, exc, None):
                    time.sleep(self._next_retry_delay(attempt, None))
                    attempt += 1
                    continue
                raise wrapped
            except Exception as exc:
                wrapped = self._wrap_network_error(exc)
                last_error = wrapped
                if attempt < max_retries and self._should_retry(None, exc, None):
                    time.sleep(self._next_retry_delay(attempt, None))
                    attempt += 1
                    continue
                raise wrapped

            if 200 <= resp.status_code < 300:
                try:
                    return resp.json()
                except Exception as exc:
                    raise BabyAPIError(
                        "Failed to parse JSON response",
                        status=resp.status_code,
                        response=resp,
                        cause=exc,
                    )

            parsed_json: Optional[Mapping[str, Any]]
            try:
                parsed = resp.json()
                parsed_json = parsed if isinstance(parsed, Mapping) else None
            except Exception:
                parsed_json = None

            error = self._parse_error(resp, parsed_json=parsed_json)
            last_error = error

            retry_after = _parse_retry_after_seconds(resp.headers)
            if attempt < max_retries and self._should_retry(resp.status_code, None, parsed_json):
                time.sleep(self._next_retry_delay(attempt, retry_after))
                attempt += 1
                continue

            raise error

        raise last_error or BabyAPIError("Request failed")

    def _post_sse(
        self,
        path: str,
        body: Mapping[str, Any],
        *,
        request_options: Optional[Union[RequestOptions, Mapping[str, Any]]] = None,
    ) -> Iterator[SSEEvent]:
        """
        OpenAI-style SSE streaming.
        NOTE: like JS SDK, this does not retry streams.
        """
        if not isinstance(body, Mapping):
            raise BabyAPIError("Request body must be a JSON object", code="INVALID_REQUEST_BODY")

        opts = self._normalize_request_options(request_options)
        api_key = opts.api_key or self.api_key
        if not api_key:
            raise BabyAPIError("API key is required (set BABYAPI_API_KEY or pass api_key)", code="API_KEY_REQUIRED")

        payload = dict(body)
        payload["stream"] = True

        headers = self._build_headers(api_key, opts.headers, extra={"Accept": "text/event-stream"})

        # Streaming timeout behavior:
        # - If user passes timeout_s in RequestOptions => use it
        # - Else => no timeout (infinite), matching JS SDK behavior
        timeout_value = None
        if opts.timeout_s is not None:
            timeout_value = self._resolve_timeout(opts.timeout_s)

        try:
            with self._client.stream("POST", path, json=payload, headers=headers, timeout=timeout_value) as resp:
                if not (200 <= resp.status_code < 300):
                    parsed_json = None
                    try:
                        parsed = resp.json()
                        parsed_json = parsed if isinstance(parsed, Mapping) else None
                    except Exception:
                        pass
                    raise self._parse_error(resp, parsed_json=parsed_json)

                for evt in parse_sse_events(_iter_sse_text(resp.iter_bytes())):
                    yield evt
                    if evt.done:
                        return
        except httpx.RequestError as exc:
            raise self._wrap_network_error(exc) from exc
        except BabyAPIError:
            raise
        except Exception as exc:
            raise self._wrap_network_error(exc) from exc

    def _parse_error(
        self,
        resp: httpx.Response,
        *,
        parsed_json: Optional[Mapping[str, Any]] = None,
        cause: Optional[BaseException] = None,
    ) -> BabyAPIError:
        status = resp.status_code
        request_id = resp.headers.get("x-request-id") or resp.headers.get("x-babyapi-request-id")

        details: Any = None
        code = None
        typ = None
        message = f"HTTP {status}"

        if parsed_json is None:
            try:
                parsed = resp.json()
                parsed_json = parsed if isinstance(parsed, Mapping) else None
                details = parsed
            except Exception:
                details = resp.text
        else:
            details = parsed_json

        # OpenAI-style error: { error: { message, type, code } }
        if isinstance(parsed_json, Mapping):
            err = parsed_json.get("error")
            if isinstance(err, Mapping):
                message = err.get("message") or message
                code_val = err.get("code")
                typ_val = err.get("type")
                code = code_val if isinstance(code_val, str) else None
                typ = typ_val if isinstance(typ_val, str) else None

        return BabyAPIError(
            message=message,
            status=status,
            code=code,
            type=typ,
            details=details,
            request_id=request_id,
            response=resp,
            cause=cause,
        )

    def _build_baby_infer_payload(self, input: BabyInferInput, extra_options: Mapping[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}

        if extra_options:
            if not isinstance(extra_options, Mapping):
                raise BabyAPIError("extra options must be a mapping", code="INVALID_INFER_INPUT")
            for k, v in extra_options.items():
                if v is not None:
                    merged[k] = v

        if isinstance(input, str):
            merged.setdefault("prompt", input)
        elif isinstance(input, Mapping):
            merged = {**dict(input), **merged}
        else:
            raise BabyAPIError("infer input must be a string or mapping", code="INVALID_INFER_INPUT")

        # prompt candidates like JS: prompt/input/text
        prompt = ""
        for candidate in (merged.get("prompt"), merged.get("input"), merged.get("text")):
            if isinstance(candidate, str):
                c = candidate.strip()
                if c:
                    prompt = c
                    break
        if not prompt:
            raise BabyAPIError("prompt is required for infer()", code="PROMPT_REQUIRED")

        # model required (or default_model)
        model_value = merged.get("model")
        model = model_value.strip() if isinstance(model_value, str) else ""
        if not model:
            model = (self.default_model or "").strip()
        if not model:
            raise BabyAPIError("model is required for infer()", code="MODEL_REQUIRED")

        # option aliases: from direct fields + optional "options" mapping
        raw_options = _pick_baby_option_fields(merged)

        if "options" in merged:
            options_payload = merged["options"]
            if not isinstance(options_payload, Mapping):
                raise BabyAPIError("options must be a mapping", code="INVALID_OPTIONS")
            for k, v in options_payload.items():
                if v is not None:
                    raw_options[k] = v

        normalized_options = _normalize_baby_options(raw_options)

        payload: Dict[str, Any] = {"model": model, "prompt": prompt}
        payload.update(normalized_options)
        return payload
