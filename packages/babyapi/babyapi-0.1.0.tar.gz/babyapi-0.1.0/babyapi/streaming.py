from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional
import json


@dataclass
class SSEEvent:
    done: bool
    data: Optional[Any]
    raw: str


def _iter_sse_text(byte_iter: Iterator[bytes]) -> Iterator[str]:
    """
    Yield decoded text chunks and normalize CRLF -> LF.
    We keep it chunk-based and let the parser handle buffering.
    """
    for chunk in byte_iter:
        if not chunk:
            continue
        text = chunk.decode("utf-8", errors="replace")
        yield text.replace("\r\n", "\n")


def parse_sse_events(text_iter: Iterator[str]) -> Iterator[SSEEvent]:
    """
    Minimal SSE "data:" parser.
    Emits SSEEvent(done=True) on [DONE].
    """
    buffer = ""
    for text in text_iter:
        buffer += text
        parts = buffer.split("\n\n")
        buffer = parts.pop() or ""
        for block in parts:
            yield from _parse_block(block)

    # best-effort flush
    rest = buffer.strip()
    if rest:
        yield from _parse_block(rest)


def _parse_block(block: str) -> Iterator[SSEEvent]:
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    data_lines = [ln[5:].strip() for ln in lines if ln.startswith("data:")]
    if not data_lines:
        return

    payload = "\n".join(data_lines)
    if payload in ("[DONE]", ""):
        yield SSEEvent(done=True, data=None, raw=payload or "[DONE]")
        return

    try:
        yield SSEEvent(done=False, data=json.loads(payload), raw=payload)
    except Exception:
        yield SSEEvent(done=False, data=None, raw=payload)
