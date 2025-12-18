"""
Tests for the asynchronous HookBridge client.
"""

import pytest
from pytest_httpx import HTTPXMock

from hookbridge import AsyncHookBridge, ValidationError

from .conftest import LIVE_MODE, MOCK_RESPONSES


class TestAsyncClientConstruction:
    """Tests for async client construction."""

    def test_requires_api_key(self) -> None:
        """Async client requires an API key."""
        with pytest.raises(ValidationError, match="API key is required"):
            AsyncHookBridge(api_key="")

    def test_custom_base_url(self) -> None:
        """Async client accepts custom base URL."""
        client = AsyncHookBridge(api_key="hb_test_xxx", base_url="https://custom.example.com")
        assert client._base_url == "https://custom.example.com"

    async def test_async_context_manager(self) -> None:
        """Async client works as async context manager."""
        async with AsyncHookBridge(api_key="hb_test_xxx") as client:
            assert client._client is not None


class TestAsyncSendWebhook:
    """Tests for sending webhooks asynchronously."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_send_basic(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Send a basic webhook."""
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/webhooks/send",
            json=MOCK_RESPONSES["send_webhook"],
        )

        result = await async_client.send(
            endpoint="https://example.com/webhook",
            payload={"event": "test"},
        )

        assert result.message_id == "019abc12-3456-7890-abcd-ef1234567890"
        assert result.status == "queued"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_send_with_idempotency_key(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Send webhook with idempotency key."""
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/webhooks/send",
            json=MOCK_RESPONSES["send_webhook"],
        )

        result = await async_client.send(
            endpoint="https://example.com/webhook",
            payload={"event": "test"},
            idempotency_key="unique-key-123",
        )

        assert result.message_id is not None


class TestAsyncGetMessage:
    """Tests for getting message details asynchronously."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_get_message(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Get message details."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/messages/{message_id}",
            json=MOCK_RESPONSES["get_message"],
        )

        message = await async_client.get_message(message_id)

        assert message.id == message_id
        assert message.status == "succeeded"


class TestAsyncMessageOperations:
    """Tests for async message operations."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_replay(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Replay a message."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/messages/{message_id}/replay",
            json={"meta": {"request_id": "req-12345"}},
        )

        await async_client.replay(message_id)

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_cancel_retry(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Cancel a pending retry."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/messages/{message_id}/cancel",
            json={"meta": {"request_id": "req-12345"}},
        )

        await async_client.cancel_retry(message_id)

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_retry_now(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Trigger immediate retry."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/messages/{message_id}/retry-now",
            json={"meta": {"request_id": "req-12345"}},
        )

        await async_client.retry_now(message_id)


class TestAsyncLogs:
    """Tests for querying logs asynchronously."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_get_logs(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Get logs."""
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/logs",
            json=MOCK_RESPONSES["get_logs"],
        )

        logs = await async_client.get_logs()

        assert len(logs.messages) == 1
        assert logs.has_more is False


class TestAsyncMetrics:
    """Tests for getting metrics asynchronously."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_get_metrics(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Get metrics."""
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/metrics?window=24h",
            json=MOCK_RESPONSES["get_metrics"],
        )

        metrics = await async_client.get_metrics()

        assert metrics.window == "24h"
        assert metrics.success_rate == 0.95


class TestAsyncDLQ:
    """Tests for async DLQ operations."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_get_dlq_messages(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Get DLQ messages."""
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/dlq/messages",
            json=MOCK_RESPONSES["get_dlq_messages"],
        )

        dlq = await async_client.get_dlq_messages()

        assert dlq.messages == []

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_replay_from_dlq(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Replay from DLQ."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/dlq/replay/{message_id}",
            json={"meta": {"request_id": "req-12345"}},
        )

        await async_client.replay_from_dlq(message_id)


class TestAsyncAPIKeys:
    """Tests for async API key management."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_list_api_keys(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """List API keys."""
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/api-keys",
            json=MOCK_RESPONSES["list_api_keys"],
        )

        keys = await async_client.list_api_keys()

        assert len(keys) == 1
        assert keys[0].key_id == "key-12345"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_create_api_key(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Create API key."""
        httpx_mock.add_response(
            method="POST",
            url=f"{async_client._base_url}/v1/api-keys",
            json=MOCK_RESPONSES["create_api_key"],
        )

        result = await async_client.create_api_key(mode="test")

        assert result.key_id == "key-new-12345"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_delete_api_key(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Delete API key."""
        key_id = "key-12345"
        httpx_mock.add_response(
            method="DELETE",
            url=f"{async_client._base_url}/v1/api-keys/{key_id}",
            json={"meta": {"request_id": "req-12345"}},
        )

        await async_client.delete_api_key(key_id)


# Live API tests
class TestAsyncLiveAPI:
    """Async tests that run against the live API."""

    @pytest.mark.live
    async def test_list_api_keys_live(self, async_client: AsyncHookBridge) -> None:
        """List API keys against live API."""
        keys = await async_client.list_api_keys()
        assert isinstance(keys, list)

    @pytest.mark.live
    async def test_get_metrics_live(self, async_client: AsyncHookBridge) -> None:
        """Get metrics against live API."""
        metrics = await async_client.get_metrics()
        assert metrics.window == "24h"

    @pytest.mark.live
    async def test_send_webhook_live(self, async_client: AsyncHookBridge, webhook_receiver_url: str) -> None:
        """Send a webhook to the test receiver."""
        import uuid

        result = await async_client.send(
            endpoint=webhook_receiver_url,
            payload={"event": "test.async_sdk", "test_id": str(uuid.uuid4())},
        )

        assert result.message_id is not None
        assert result.status == "queued"

    @pytest.mark.live
    async def test_get_message_live(self, async_client: AsyncHookBridge, webhook_receiver_url: str) -> None:
        """Send and retrieve a message."""
        import asyncio
        import uuid

        result = await async_client.send(
            endpoint=webhook_receiver_url,
            payload={"event": "test.async_get_message", "test_id": str(uuid.uuid4())},
        )

        await asyncio.sleep(1)

        message = await async_client.get_message(result.message_id)
        assert message.id == result.message_id

    @pytest.mark.live
    async def test_get_logs_live(self, async_client: AsyncHookBridge) -> None:
        """Get logs."""
        logs = await async_client.get_logs(limit=10)
        assert isinstance(logs.messages, list)
