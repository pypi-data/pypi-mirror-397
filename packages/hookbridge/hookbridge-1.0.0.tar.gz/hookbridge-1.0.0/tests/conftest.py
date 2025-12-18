"""
Pytest configuration and fixtures for HookBridge SDK tests.

Test modes:
- Mock mode (default): Uses pytest-httpx to mock HTTP responses
- Live mode: Set HOOKBRIDGE_API_KEY env var to test against real API

For local testing against the testing environment:
    export HOOKBRIDGE_API_KEY=your_test_key
    export HOOKBRIDGE_BASE_URL=https://localhost/api
    pytest
"""

import os
from typing import Any, Generator

import pytest

from hookbridge import HookBridge, AsyncHookBridge


# Check if we're running in live mode
LIVE_MODE = bool(os.environ.get("HOOKBRIDGE_API_KEY"))


def pytest_configure(config: Any) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "live: mark test as requiring live API access"
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Skip live tests when not in live mode."""
    if LIVE_MODE:
        return

    skip_live = pytest.mark.skip(reason="Live tests require HOOKBRIDGE_API_KEY env var")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture
def api_key() -> str:
    """Get API key for testing."""
    if LIVE_MODE:
        return os.environ["HOOKBRIDGE_API_KEY"]
    return "hb_test_mock_api_key_for_testing"


@pytest.fixture
def base_url() -> str:
    """Get base URL for testing."""
    return os.environ.get("HOOKBRIDGE_BASE_URL", "https://api.hookbridge.io")


@pytest.fixture
def webhook_receiver_url() -> str:
    """Get webhook receiver URL for live testing.

    Must be set via HOOKBRIDGE_RECEIVER_URL env var for live tests.
    """
    url = os.environ.get("HOOKBRIDGE_RECEIVER_URL")
    if LIVE_MODE and not url:
        pytest.skip("Live webhook tests require HOOKBRIDGE_RECEIVER_URL env var")
    return url or "https://example.com/webhook"


@pytest.fixture
def client(api_key: str, base_url: str) -> Generator[HookBridge, None, None]:
    """Create a sync HookBridge client."""
    with HookBridge(api_key=api_key, base_url=base_url) as client:
        yield client


@pytest.fixture
async def async_client(api_key: str, base_url: str) -> AsyncHookBridge:
    """Create an async HookBridge client."""
    async with AsyncHookBridge(api_key=api_key, base_url=base_url) as client:
        yield client


# Standard mock responses for use in tests
MOCK_RESPONSES = {
    "send_webhook": {
        "data": {
            "message_id": "019abc12-3456-7890-abcd-ef1234567890",
            "status": "queued",
        },
        "meta": {"request_id": "req-12345"},
    },
    "get_message": {
        "data": {
            "id": "019abc12-3456-7890-abcd-ef1234567890",
            "project_id": "proj-12345",
            "endpoint_id": "ep-12345",
            "status": "succeeded",
            "attempt_count": 1,
            "replay_count": 0,
            "content_type": "application/json",
            "size_bytes": 256,
            "payload_sha256": "abc123",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:01Z",
            "response_status": 200,
            "response_latency_ms": 50,
        },
        "meta": {"request_id": "req-12345"},
    },
    "get_logs": {
        "data": [
            {
                "message_id": "019abc12-3456-7890-abcd-ef1234567890",
                "endpoint": "https://example.com/webhook",
                "status": "succeeded",
                "attempt_count": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "delivered_at": "2025-01-01T00:00:01Z",
                "response_status": 200,
                "response_latency_ms": 50,
            }
        ],
        "meta": {"has_more": False, "request_id": "req-12345"},
    },
    "get_metrics": {
        "data": {
            "window": "24h",
            "total_messages": 100,
            "succeeded": 95,
            "failed": 5,
            "retries": 10,
            "success_rate": 0.95,
            "avg_latency_ms": 120,
        },
        "meta": {"request_id": "req-12345"},
    },
    "get_dlq_messages": {
        "data": {
            "messages": [],
            "has_more": False,
        },
        "meta": {"request_id": "req-12345"},
    },
    "list_api_keys": {
        "data": [
            {
                "key_id": "key-12345",
                "label": "test-key",
                "prefix": "hb_test_abc",
                "created_at": "2025-01-01T00:00:00Z",
                "last_used_at": "2025-01-01T12:00:00Z",
            }
        ],
        "meta": {"request_id": "req-12345"},
    },
    "create_api_key": {
        "data": {
            "key_id": "key-new-12345",
            "key": "hb_test_new_key_value",
            "prefix": "hb_test_new",
            "label": "new-key",
            "created_at": "2025-01-01T00:00:00Z",
        },
        "meta": {"request_id": "req-12345"},
    },
}

# Error responses
MOCK_ERROR_RESPONSES = {
    "unauthorized": {
        "status_code": 401,
        "json": {
            "error": {"code": "UNAUTHORIZED", "message": "Invalid API key"},
            "meta": {"request_id": "req-12345"},
        },
    },
    "not_found": {
        "status_code": 404,
        "json": {
            "error": {"code": "NOT_FOUND", "message": "Message not found"},
            "meta": {"request_id": "req-12345"},
        },
    },
    "rate_limit": {
        "status_code": 429,
        "json": {
            "error": {"code": "RATE_LIMITED", "message": "Too many requests"},
            "meta": {"request_id": "req-12345"},
        },
        "headers": {"Retry-After": "60"},
    },
    "validation": {
        "status_code": 400,
        "json": {
            "error": {"code": "VALIDATION_ERROR", "message": "Invalid endpoint URL"},
            "meta": {"request_id": "req-12345"},
        },
    },
    "idempotency": {
        "status_code": 409,
        "json": {
            "error": {"code": "IDEMPOTENCY_MISMATCH", "message": "Idempotency key mismatch"},
            "meta": {"request_id": "req-12345"},
        },
    },
    "replay_limit": {
        "status_code": 429,
        "json": {
            "error": {"code": "REPLAY_LIMIT_EXCEEDED", "message": "Replay limit exceeded"},
            "meta": {"request_id": "req-12345"},
        },
    },
}
