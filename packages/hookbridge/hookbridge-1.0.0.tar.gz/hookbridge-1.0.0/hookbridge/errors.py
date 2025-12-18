"""
HookBridge SDK Errors
"""

from typing import Optional


class HookBridgeError(Exception):
    """Base error class for HookBridge SDK errors."""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        request_id: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.request_id = request_id
        self.status_code = status_code

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.code:
            parts.append(f"code={self.code}")
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        return " ".join(parts)


class AuthenticationError(HookBridgeError):
    """Error thrown when authentication fails."""

    def __init__(
        self,
        message: str = "Invalid or missing API key",
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, "UNAUTHORIZED", request_id, 401)


class NotFoundError(HookBridgeError):
    """Error thrown when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, "NOT_FOUND", request_id, 404)


class ValidationError(HookBridgeError):
    """Error thrown when request validation fails."""

    def __init__(
        self,
        message: str,
        code: str = "INVALID_REQUEST",
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, code, request_id, 400)


class RateLimitError(HookBridgeError):
    """Error thrown when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, "RATE_LIMIT_EXCEEDED", request_id, 429)
        self.retry_after = retry_after


class IdempotencyError(HookBridgeError):
    """Error thrown for idempotency conflicts."""

    def __init__(
        self,
        message: str = "Idempotency key already used with different payload",
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, "IDEMPOTENCY_MISMATCH", request_id, 409)


class ReplayLimitError(HookBridgeError):
    """Error thrown when replay limit is exceeded."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, "REPLAY_LIMIT_EXCEEDED", request_id, 429)


class NetworkError(HookBridgeError):
    """Error thrown for network/connection issues."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "NETWORK_ERROR")


class TimeoutError(HookBridgeError):
    """Error thrown when request times out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, "TIMEOUT")
