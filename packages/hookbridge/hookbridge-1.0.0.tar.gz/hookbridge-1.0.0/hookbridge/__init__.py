"""
HookBridge SDK for Python

Send webhooks with guaranteed delivery, automatic retries, and full observability.

Example:
    >>> from hookbridge import HookBridge
    >>>
    >>> client = HookBridge(api_key="hb_live_xxxxxxxxxxxxxxxxxxxx")
    >>>
    >>> result = client.send(
    ...     endpoint="https://customer.app/webhooks",
    ...     payload={"event": "order.created", "order_id": "12345"}
    ... )
    >>> print(result.message_id)
"""

from hookbridge.client import HookBridge, AsyncHookBridge
from hookbridge.types import (
    SendWebhookResponse,
    Message,
    MessageSummary,
    MessageStatus,
    LogsResponse,
    Metrics,
    MetricsWindow,
    APIKeyInfo,
    APIKeyMode,
    CreateAPIKeyResponse,
    DLQMessagesResponse,
)
from hookbridge.errors import (
    HookBridgeError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    IdempotencyError,
    ReplayLimitError,
    NetworkError,
    TimeoutError,
)

__version__ = "1.0.0"

__all__ = [
    # Client
    "HookBridge",
    "AsyncHookBridge",
    # Types
    "SendWebhookResponse",
    "Message",
    "MessageSummary",
    "MessageStatus",
    "LogsResponse",
    "Metrics",
    "MetricsWindow",
    "APIKeyInfo",
    "APIKeyMode",
    "CreateAPIKeyResponse",
    "DLQMessagesResponse",
    # Errors
    "HookBridgeError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "IdempotencyError",
    "ReplayLimitError",
    "NetworkError",
    "TimeoutError",
]
