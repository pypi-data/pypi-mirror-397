"""
Tests for error handling in the HookBridge SDK.
"""

import pytest
from pytest_httpx import HTTPXMock

from hookbridge import (
    HookBridge,
    AsyncHookBridge,
    HookBridgeError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    IdempotencyError,
    ReplayLimitError,
    ValidationError,
)

from .conftest import LIVE_MODE, MOCK_ERROR_RESPONSES


class TestErrorClasses:
    """Tests for error class structure."""

    def test_hookbridge_error_base(self) -> None:
        """HookBridgeError is the base error class."""
        error = HookBridgeError("Test error", "TEST_CODE", "req-123", 500)
        assert "Test error" in str(error)
        assert "TEST_CODE" in str(error)
        assert "req-123" in str(error)
        assert error.code == "TEST_CODE"
        assert error.request_id == "req-123"
        assert error.status_code == 500

    def test_authentication_error(self) -> None:
        """AuthenticationError for 401 responses."""
        error = AuthenticationError("Invalid API key", "req-123")
        assert isinstance(error, HookBridgeError)
        assert error.status_code == 401

    def test_not_found_error(self) -> None:
        """NotFoundError for 404 responses."""
        error = NotFoundError("Message not found", "req-123")
        assert isinstance(error, HookBridgeError)
        assert error.status_code == 404

    def test_rate_limit_error(self) -> None:
        """RateLimitError for 429 responses."""
        error = RateLimitError("Too many requests", "req-123", retry_after=60)
        assert isinstance(error, HookBridgeError)
        assert error.status_code == 429
        assert error.retry_after == 60

    def test_rate_limit_error_no_retry_after(self) -> None:
        """RateLimitError without retry-after."""
        error = RateLimitError("Too many requests", "req-123")
        assert error.retry_after is None

    def test_idempotency_error(self) -> None:
        """IdempotencyError for idempotency key conflicts."""
        error = IdempotencyError("Key mismatch", "req-123")
        assert isinstance(error, HookBridgeError)
        assert error.status_code == 409

    def test_replay_limit_error(self) -> None:
        """ReplayLimitError when replay limit exceeded."""
        error = ReplayLimitError("Limit exceeded", "req-123")
        assert isinstance(error, HookBridgeError)
        assert error.status_code == 429

    def test_validation_error(self) -> None:
        """ValidationError for client-side validation."""
        error = ValidationError("API key is required")
        assert isinstance(error, HookBridgeError)
        assert "API key is required" in str(error)


class TestSyncErrorHandling:
    """Tests for error handling in sync client."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_authentication_error_response(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """401 response raises AuthenticationError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/api-keys",
            status_code=401,
            json=MOCK_ERROR_RESPONSES["unauthorized"]["json"],
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client.list_api_keys()

        assert exc_info.value.status_code == 401
        assert exc_info.value.request_id == "req-12345"

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_not_found_error_response(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """404 response raises NotFoundError."""
        message_id = "nonexistent"
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/messages/{message_id}",
            status_code=404,
            json=MOCK_ERROR_RESPONSES["not_found"]["json"],
        )

        with pytest.raises(NotFoundError) as exc_info:
            client.get_message(message_id)

        assert exc_info.value.status_code == 404

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_rate_limit_error_response(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """429 response raises RateLimitError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/api-keys",
            status_code=429,
            json=MOCK_ERROR_RESPONSES["rate_limit"]["json"],
            headers={"Retry-After": "60"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.list_api_keys()

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_idempotency_error_response(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """409 with IDEMPOTENCY_MISMATCH raises IdempotencyError."""
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/webhooks/send",
            status_code=409,
            json=MOCK_ERROR_RESPONSES["idempotency"]["json"],
        )

        with pytest.raises(IdempotencyError):
            client.send(
                endpoint="https://example.com/webhook",
                payload={"event": "test"},
                idempotency_key="duplicate-key",
            )

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_replay_limit_error_response(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """429 with REPLAY_LIMIT_EXCEEDED raises ReplayLimitError."""
        message_id = "019abc12-3456-7890-abcd-ef1234567890"
        httpx_mock.add_response(
            method="POST",
            url=f"{client._base_url}/v1/messages/{message_id}/replay",
            status_code=429,
            json=MOCK_ERROR_RESPONSES["replay_limit"]["json"],
        )

        with pytest.raises(ReplayLimitError):
            client.replay(message_id)

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_generic_error_response(
        self, client: HookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """Other errors raise HookBridgeError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/api-keys",
            status_code=500,
            json={
                "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong"},
                "meta": {"request_id": "req-12345"},
            },
        )

        with pytest.raises(HookBridgeError) as exc_info:
            client.list_api_keys()

        assert exc_info.value.status_code == 500
        assert exc_info.value.code == "INTERNAL_ERROR"


class TestAsyncErrorHandling:
    """Tests for error handling in async client."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_authentication_error_response(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """401 response raises AuthenticationError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/api-keys",
            status_code=401,
            json=MOCK_ERROR_RESPONSES["unauthorized"]["json"],
        )

        with pytest.raises(AuthenticationError):
            await async_client.list_api_keys()

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_not_found_error_response(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """404 response raises NotFoundError."""
        message_id = "nonexistent"
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/messages/{message_id}",
            status_code=404,
            json=MOCK_ERROR_RESPONSES["not_found"]["json"],
        )

        with pytest.raises(NotFoundError):
            await async_client.get_message(message_id)

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    async def test_rate_limit_error_response(
        self, async_client: AsyncHookBridge, httpx_mock: HTTPXMock
    ) -> None:
        """429 response raises RateLimitError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{async_client._base_url}/v1/api-keys",
            status_code=429,
            json=MOCK_ERROR_RESPONSES["rate_limit"]["json"],
            headers={"Retry-After": "30"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            await async_client.list_api_keys()

        assert exc_info.value.retry_after == 30


class TestRetryBehavior:
    """Tests for retry behavior on errors."""

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_no_retry_on_4xx(self, client: HookBridge, httpx_mock: HTTPXMock) -> None:
        """4xx errors are not retried."""
        httpx_mock.add_response(
            method="GET",
            url=f"{client._base_url}/v1/api-keys",
            status_code=400,
            json=MOCK_ERROR_RESPONSES["validation"]["json"],
        )

        with pytest.raises(HookBridgeError):
            client.list_api_keys()

        # Should only have made one request (no retries)
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_retry_on_5xx(self, httpx_mock: HTTPXMock) -> None:
        """5xx errors are retried."""
        # Create client with 2 retries
        with HookBridge(api_key="hb_test_xxx", retries=2) as client:
            # All attempts fail with 500
            httpx_mock.add_response(
                method="GET",
                url=f"{client._base_url}/v1/api-keys",
                status_code=500,
                json={
                    "error": {"code": "INTERNAL_ERROR", "message": "Server error"},
                    "meta": {"request_id": "req-12345"},
                },
            )
            httpx_mock.add_response(
                method="GET",
                url=f"{client._base_url}/v1/api-keys",
                status_code=500,
                json={
                    "error": {"code": "INTERNAL_ERROR", "message": "Server error"},
                    "meta": {"request_id": "req-12345"},
                },
            )
            httpx_mock.add_response(
                method="GET",
                url=f"{client._base_url}/v1/api-keys",
                status_code=500,
                json={
                    "error": {"code": "INTERNAL_ERROR", "message": "Server error"},
                    "meta": {"request_id": "req-12345"},
                },
            )

            with pytest.raises(HookBridgeError):
                client.list_api_keys()

            # Should have made 3 requests (1 initial + 2 retries)
            assert len(httpx_mock.get_requests()) == 3

    @pytest.mark.skipif(LIVE_MODE, reason="Mock test only")
    def test_retry_succeeds_after_failure(
        self, httpx_mock: HTTPXMock
    ) -> None:
        """Request succeeds after initial failure."""
        with HookBridge(api_key="hb_test_xxx", retries=2) as client:
            # First request fails, second succeeds
            httpx_mock.add_response(
                method="GET",
                url=f"{client._base_url}/v1/api-keys",
                status_code=500,
                json={
                    "error": {"code": "INTERNAL_ERROR", "message": "Server error"},
                    "meta": {"request_id": "req-12345"},
                },
            )
            httpx_mock.add_response(
                method="GET",
                url=f"{client._base_url}/v1/api-keys",
                json={
                    "data": [],
                    "meta": {"request_id": "req-12345"},
                },
            )

            keys = client.list_api_keys()
            assert keys == []
            assert len(httpx_mock.get_requests()) == 2
