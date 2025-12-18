"""
Tests for the synchronous HookBridge client.
"""

import pytest
from pytest_httpx import HTTPXMock

from hookbridge import HookBridge, ValidationError
from hookbridge.types import MessageStatus

from .conftest import LIVE_MODE, MOCK_RESPONSES


class TestClientConstruction:
    """Tests for client construction and configuration."""

    def test_requires_api_key(self) -> None:
        """Client requires an API key."""
        with pytest.raises(ValidationError, match="API key is required"):
            HookBridge(api_key="")

    def test_default_base_url(self) -> None:
        """Client uses default base URL when not specified."""
        client = HookBridge(api_key="hb_test_xxx")
        # The default comes from env var or falls back to production
        assert "hookbridge.io" in client._base_url or "HOOKBRIDGE_BASE_URL" in str(
            client._base_url
        )
        client.close()

    def test_custom_base_url(self) -> None:
        """Client accepts custom base URL."""
        client = HookBridge(api_key="hb_test_xxx", base_url="https://custom.example.com")
        assert client._base_url == "https://custom.example.com"
        client.close()

    def test_base_url_strips_trailing_slash(self) -> None:
        """Base URL trailing slash is stripped."""
        client = HookBridge(api_key="hb_test_xxx", base_url="https://example.com/")
        assert client._base_url == "https://example.com"
        client.close()

    def test_custom_timeout(self) -> None:
        """Client accepts custom timeout."""
        client = HookBridge(api_key="hb_test_xxx", timeout=60.0)
        assert client._timeout == 60.0
        client.close()

    def test_custom_retries(self) -> None:
        """Client accepts custom retry count."""
        client = HookBridge(api_key="hb_test_xxx", retries=5)
        assert client._retries == 5
        client.close()

    def test_context_manager(self) -> None:
        """Client works as context manager."""
        with HookBridge(api_key="hb_test_xxx") as client:
            assert client._client is not None


class TestSendWebhook:
    """Tests for sending webhooks."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_send_basic(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Send a basic webhook."""
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/webhooks/send",
            json=MOCK_RESPONSES["send_webhook"],
        )

        result = client.send(
            endpoint="https://example.com/webhook",
            payload={"event": "test"},
        )

        assert result.message_id == "019abc12-3456-7890-abcd-ef1234567890"
        assert result.status == "queued"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_send_with_headers(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Send webhook with custom headers."""
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/webhooks/send",
            json=MOCK_RESPONSES["send_webhook"],
        )

        result = client.send(
            endpoint="https://example.com/webhook",
            payload={"event": "test"},
            headers={"X-Custom": "value"},
        )

        assert result.message_id is not None

        # Verify the request included custom headers in the body
        request = httpx_mock.get_request()
        assert request is not None
        import json

        body = json.loads(request.content)
        assert body["headers"] == {"X-Custom": "value"}

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_send_with_idempotency_key(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Send webhook with idempotency key."""
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/webhooks/send",
            json=MOCK_RESPONSES["send_webhook"],
        )

        result = client.send(
            endpoint="https://example.com/webhook",
            payload={"event": "test"},
            idempotency_key="unique-key-123",
        )

        assert result.message_id is not None

        request = httpx_mock.get_request()
        assert request is not None
        import json

        body = json.loads(request.content)
        assert body["idempotency_key"] == "unique-key-123"


class TestGetMessage:
    """Tests for getting message details."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_get_message(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Get message details."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/messages/{message_id}",
            json=MOCK_RESPONSES["get_message"],
        )

        message = client.get_message(message_id)

        assert message.id == message_id
        assert message.status == "succeeded"
        assert message.attempt_count == 1
        assert message.response_status == 200


class TestMessageOperations:
    """Tests for message operations (replay, cancel, retry-now)."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_replay(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Replay a message."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/messages/{message_id}/replay",
            json={"meta": {"request_id": "req-12345"}},
        )

        # Should not raise
        client.replay(message_id)

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_cancel_retry(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Cancel a pending retry."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/messages/{message_id}/cancel",
            json={"meta": {"request_id": "req-12345"}},
        )

        client.cancel_retry(message_id)

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_retry_now(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Trigger immediate retry."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/messages/{message_id}/retry-now",
            json={"meta": {"request_id": "req-12345"}},
        )

        client.retry_now(message_id)


class TestLogs:
    """Tests for querying logs."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_get_logs_basic(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Get logs without filters."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/logs",
            json=MOCK_RESPONSES["get_logs"],
        )

        logs = client.get_logs()

        assert len(logs.messages) == 1
        assert logs.messages[0].status == "succeeded"
        assert logs.has_more is False

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_get_logs_with_status_filter(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Get logs filtered by status."""
        httpx_mock.add_response(
            method="GET",
            json=MOCK_RESPONSES["get_logs"],
        )

        logs = client.get_logs(status="succeeded")

        request = httpx_mock.get_request()
        assert request is not None
        assert "status=succeeded" in str(request.url)


class TestMetrics:
    """Tests for getting metrics."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_get_metrics_default(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Get metrics with default window."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/metrics?window=24h",
            json=MOCK_RESPONSES["get_metrics"],
        )

        metrics = client.get_metrics()

        assert metrics.window == "24h"
        assert metrics.total_messages == 100
        assert metrics.success_rate == 0.95

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_get_metrics_custom_window(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Get metrics with custom window."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/metrics?window=7d",
            json={**MOCK_RESPONSES["get_metrics"], "data": {**MOCK_RESPONSES["get_metrics"]["data"], "window": "7d"}},
        )

        metrics = client.get_metrics(window="7d")

        assert metrics.window == "7d"


class TestDLQ:
    """Tests for Dead Letter Queue operations."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_get_dlq_messages(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Get DLQ messages."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/dlq/messages",
            json=MOCK_RESPONSES["get_dlq_messages"],
        )

        dlq = client.get_dlq_messages()

        assert dlq.messages == []
        assert dlq.has_more is False

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_replay_from_dlq(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Replay message from DLQ."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/dlq/replay/{message_id}",
            json={"meta": {"request_id": "req-12345"}},
        )

        client.replay_from_dlq(message_id)


class TestAPIKeys:
    """Tests for API key management."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_list_api_keys(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """List API keys."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/api-keys",
            json=MOCK_RESPONSES["list_api_keys"],
        )

        keys = client.list_api_keys()

        assert len(keys) == 1
        assert keys[0].key_id == "key-12345"
        assert keys[0].label == "test-key"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_create_api_key(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Create a new API key."""
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/api-keys",
            json=MOCK_RESPONSES["create_api_key"],
        )

        result = client.create_api_key(mode="test", label="new-key")

        assert result.key_id == "key-new-12345"
        assert result.key == "hb_test_new_key_value"
        assert result.label == "new-key"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_delete_api_key(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """Delete an API key."""
        key_id = "key-12345"
        httpx_mock.add_response(
            method="DELETE",
            url=f"{client._base_url}/v1/api-keys/{key_id}",
            json={"meta": {"request_id": "req-12345"}},
        )

        client.delete_api_key(key_id)


# Live API tests - only run when HOOKBRIDGE_API_KEY is set
class TestLiveAPI:
    """Tests that run against the live API."""

    @pytest.mark.live
    def test_list_api_keys_live(self, client: HookBridge) -> None:
        """List API keys against live API."""
        keys = client.list_api_keys()
        assert isinstance(keys, list)

    @pytest.mark.live
    def test_get_metrics_live(self, client: HookBridge) -> None:
        """Get metrics against live API."""
        metrics = client.get_metrics()
        assert metrics.window == "24h"
        assert isinstance(metrics.total_messages, int)

    @pytest.mark.live
    def test_get_logs_live(self, client: HookBridge) -> None:
        """Get logs against live API."""
        logs = client.get_logs(limit=10)
        assert isinstance(logs.messages, list)
        assert isinstance(logs.has_more, bool)

    @pytest.mark.live
    def test_send_webhook_live(self, client: HookBridge, webhook_receiver_url: str) -> None:
        """Send a webhook to the test receiver."""
        import uuid

        result = client.send(
            endpoint=webhook_receiver_url,
            payload={"event": "test.sdk", "test_id": str(uuid.uuid4())},
        )

        assert result.message_id is not None
        assert result.status == "queued"

    @pytest.mark.live
    def test_send_webhook_with_idempotency_key_live(self, client: HookBridge, webhook_receiver_url: str) -> None:
        """Send webhook with idempotency key."""
        import uuid

        idempotency_key = f"test-{uuid.uuid4()}"

        result = client.send(
            endpoint=webhook_receiver_url,
            payload={"event": "test.idempotency"},
            idempotency_key=idempotency_key,
        )

        assert result.message_id is not None

    @pytest.mark.live
    def test_get_message_live(self, client: HookBridge, webhook_receiver_url: str) -> None:
        """Send and then retrieve a message."""
        import time
        import uuid

        # Send a webhook first
        result = client.send(
            endpoint=webhook_receiver_url,
            payload={"event": "test.get_message", "test_id": str(uuid.uuid4())},
        )

        # Wait a moment for processing
        time.sleep(1)

        # Get the message details
        message = client.get_message(result.message_id)

        assert message.id == result.message_id
        assert message.status in ["queued", "delivering", "succeeded", "pending_retry"]

    @pytest.mark.live
    def test_get_dlq_messages_live(self, client: HookBridge) -> None:
        """Get DLQ messages."""
        dlq = client.get_dlq_messages(limit=10)
        assert isinstance(dlq.messages, list)
        assert isinstance(dlq.has_more, bool)
