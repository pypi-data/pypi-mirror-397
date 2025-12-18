"""
HookBridge SDK Types
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

# Type aliases
MessageStatus = Literal["queued", "delivering", "succeeded", "pending_retry", "failed_permanent"]
MetricsWindow = Literal["1h", "24h", "7d", "30d"]
APIKeyMode = Literal["live", "test"]


@dataclass(frozen=True)
class SendWebhookResponse:
    """Response from sending a webhook."""

    message_id: str
    """Unique message identifier (UUIDv7)."""

    status: Literal["queued"]
    """Initial message status."""


@dataclass(frozen=True)
class Message:
    """Detailed message information."""

    id: str
    """Unique message identifier (UUIDv7)."""

    project_id: str
    """Project that owns this message."""

    endpoint_id: str
    """Endpoint ID for delivery."""

    status: MessageStatus
    """Current message status."""

    attempt_count: int
    """Number of delivery attempts made."""

    replay_count: int
    """Number of times manually replayed."""

    content_type: str
    """Content-Type header used for delivery."""

    size_bytes: int
    """Payload size in bytes."""

    payload_sha256: str
    """SHA256 hash of the payload."""

    created_at: datetime
    """When the message was created."""

    updated_at: datetime
    """When the message was last updated."""

    idempotency_key: Optional[str] = None
    """Idempotency key if provided."""

    next_attempt_at: Optional[datetime] = None
    """Scheduled time for next retry attempt."""

    last_error: Optional[str] = None
    """Error message from last failed attempt."""

    response_status: Optional[int] = None
    """HTTP status code from most recent attempt."""

    response_latency_ms: Optional[int] = None
    """Latency in ms for most recent attempt."""


@dataclass(frozen=True)
class MessageSummary:
    """Summary of a message (used in logs)."""

    message_id: str
    """Message ID."""

    endpoint: str
    """Endpoint URL."""

    status: MessageStatus
    """Current status."""

    attempt_count: int
    """Number of attempts."""

    created_at: datetime
    """When created."""

    delivered_at: Optional[datetime] = None
    """When delivered (if succeeded)."""

    response_status: Optional[int] = None
    """HTTP response status."""

    response_latency_ms: Optional[int] = None
    """Response latency in ms."""

    last_error: Optional[str] = None
    """Last error message."""


@dataclass(frozen=True)
class LogsResponse:
    """Response from querying logs."""

    messages: list[MessageSummary]
    """Array of message summaries."""

    has_more: bool
    """Whether more results are available."""

    next_cursor: Optional[str] = None
    """Cursor for next page."""


@dataclass(frozen=True)
class DLQMessagesResponse:
    """Response from querying DLQ messages."""

    messages: list[MessageSummary]
    """Array of failed messages."""

    has_more: bool
    """Whether more results are available."""

    next_cursor: Optional[str] = None
    """Cursor for next page."""


@dataclass(frozen=True)
class Metrics:
    """Aggregated delivery metrics."""

    window: MetricsWindow
    """Time window for these metrics."""

    total_messages: int
    """Total number of messages."""

    succeeded: int
    """Successfully delivered messages."""

    failed: int
    """Permanently failed messages."""

    retries: int
    """Total retry attempts."""

    success_rate: float
    """Success rate (0-1)."""

    avg_latency_ms: int
    """Average latency in ms."""


@dataclass(frozen=True)
class APIKeyInfo:
    """API key information."""

    key_id: str
    """Unique key identifier."""

    label: str
    """Human-readable label."""

    prefix: str
    """First 11 characters of the key."""

    created_at: datetime
    """When the key was created."""

    last_used_at: Optional[datetime] = None
    """Last time the key was used."""


@dataclass(frozen=True)
class CreateAPIKeyResponse:
    """Response from creating an API key."""

    key_id: str
    """Unique key identifier."""

    key: str
    """The full API key (shown only once!)."""

    prefix: str
    """First 11 characters of the key."""

    label: str
    """Human-readable label."""

    created_at: datetime
    """When the key was created."""
