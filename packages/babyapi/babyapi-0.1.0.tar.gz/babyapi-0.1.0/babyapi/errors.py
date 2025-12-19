from __future__ import annotations
from typing import Any, Optional


class BabyAPIError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        type: Optional[str] = None,
        details: Any = None,
        request_id: Optional[str] = None,
        response: Any = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.type = type
        self.details = details
        self.request_id = request_id
        self.response = response
        self.cause = cause
        if cause is not None:
            self.__cause__ = cause

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        bits = [self.message]
        if self.status is not None:
            bits.append(f"(status={self.status})")
        if self.code:
            bits.append(f"(code={self.code})")
        return " ".join(bits)
