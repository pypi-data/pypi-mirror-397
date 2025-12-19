from __future__ import annotations

from typing import Any, Dict, Iterator, Optional, TYPE_CHECKING
from .streaming import SSEEvent

if TYPE_CHECKING:  # pragma: no cover
    from .client import BabyAPI, RequestOptions, BabyInferInput


class CompletionsResource:
    def __init__(self, client: "BabyAPI"):
        self._client = client

    def create(self, *, request_options: Optional["RequestOptions"] = None, **body: Any) -> Dict[str, Any]:
        return self._client._post_json("/v1/completions", body, request_options=request_options)

    def stream(self, *, request_options: Optional["RequestOptions"] = None, **body: Any) -> Iterator[SSEEvent]:
        return self._client._post_sse("/v1/completions", body, request_options=request_options)


class ChatCompletionsResource:
    def __init__(self, client: "BabyAPI"):
        self._client = client

    def create(self, *, request_options: Optional["RequestOptions"] = None, **body: Any) -> Dict[str, Any]:
        return self._client._post_json("/v1/chat/completions", body, request_options=request_options)

    def stream(self, *, request_options: Optional["RequestOptions"] = None, **body: Any) -> Iterator[SSEEvent]:
        return self._client._post_sse("/v1/chat/completions", body, request_options=request_options)


class ChatResource:
    def __init__(self, client: "BabyAPI"):
        self.completions = ChatCompletionsResource(client)


class BabyResource:
    def __init__(self, client: "BabyAPI"):
        self._client = client

    def infer(
        self,
        input: "BabyInferInput",
        *,
        request_options: Optional["RequestOptions"] = None,
        **extra_options: Any,
    ) -> Dict[str, Any]:
        payload = self._client._build_baby_infer_payload(input, extra_options)
        return self._client._post_json("/infer", payload, request_options=request_options)
