"""
HookBridge SDK Client
"""

import os
from datetime import datetime
from typing import Any, Optional, Union
from urllib.parse import urlencode

import httpx

from hookbridge.errors import (
    AuthenticationError,
    HookBridgeError,
    IdempotencyError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ReplayLimitError,
    TimeoutError,
    ValidationError,
)
from hookbridge.types import (
    APIKeyInfo,
    APIKeyMode,
    CreateAPIKeyResponse,
    DLQMessagesResponse,
    LogsResponse,
    Message,
    MessageStatus,
    MessageSummary,
    Metrics,
    MetricsWindow,
    SendWebhookResponse,
)

DEFAULT_BASE_URL = os.environ.get("HOOKBRIDGE_BASE_URL", "https://api.hookbridge.io")
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3


class HookBridge:
    """
    HookBridge API client (synchronous).

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

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        """
        Create a new HookBridge client.

        Args:
            api_key: Your HookBridge API key (starts with hb_live_ or hb_test_)
            base_url: Base URL for the API (default: https://api.hookbridge.io)
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retries for failed requests (default: 3)
        """
        if not api_key:
            raise ValidationError("API key is required")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = retries
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "hookbridge-python/1.0.0",
            },
        )

    def __enter__(self) -> "HookBridge":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def send(
        self,
        endpoint: str,
        payload: dict[str, Any],
        *,
        headers: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SendWebhookResponse:
        """
        Send a webhook for delivery.

        Args:
            endpoint: HTTPS URL of the webhook endpoint
            payload: JSON payload to send (max 1 MB)
            headers: Optional custom headers to include
            idempotency_key: Optional key to prevent duplicate sends

        Returns:
            SendWebhookResponse with message_id and status

        Example:
            >>> result = client.send(
            ...     endpoint="https://customer.app/webhooks",
            ...     payload={"event": "order.created"},
            ...     idempotency_key="order-123-created"
            ... )
        """
        body = {
            "endpoint": endpoint,
            "payload": payload,
        }
        if headers:
            body["headers"] = headers
        if idempotency_key:
            body["idempotency_key"] = idempotency_key

        response = self._request("POST", "/v1/webhooks/send", json=body)
        data = response["data"]

        return SendWebhookResponse(
            message_id=data["message_id"],
            status=data["status"],
        )

    def get_message(self, message_id: str) -> Message:
        """
        Get details for a specific message.

        Args:
            message_id: The message ID to retrieve

        Returns:
            Message with full details
        """
        response = self._request("GET", f"/v1/messages/{message_id}")
        return self._parse_message(response["data"])

    def replay(self, message_id: str) -> None:
        """
        Replay a message for redelivery.

        Args:
            message_id: The message ID to replay
        """
        self._request("POST", f"/v1/messages/{message_id}/replay")

    def cancel_retry(self, message_id: str) -> None:
        """
        Cancel a pending retry.

        Args:
            message_id: The message ID to cancel
        """
        self._request("POST", f"/v1/messages/{message_id}/cancel")

    def retry_now(self, message_id: str) -> None:
        """
        Trigger an immediate retry for a pending message.

        Args:
            message_id: The message ID to retry
        """
        self._request("POST", f"/v1/messages/{message_id}/retry-now")

    def get_logs(
        self,
        *,
        status: Optional[MessageStatus] = None,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LogsResponse:
        """
        Query delivery logs with optional filters.

        Args:
            status: Filter by message status
            start_time: Filter messages created after this time
            end_time: Filter messages created before this time
            limit: Maximum results to return (1-500, default 50)
            cursor: Pagination cursor from previous response

        Returns:
            LogsResponse with messages, has_more, and next_cursor
        """
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if start_time:
            params["start_time"] = (
                start_time.isoformat() if isinstance(start_time, datetime) else start_time
            )
        if end_time:
            params["end_time"] = (
                end_time.isoformat() if isinstance(end_time, datetime) else end_time
            )
        if limit:
            params["limit"] = str(limit)
        if cursor:
            params["cursor"] = cursor

        path = "/v1/logs"
        if params:
            path = f"{path}?{urlencode(params)}"

        response = self._request("GET", path)
        return LogsResponse(
            messages=[self._parse_message_summary(m) for m in response["data"]],
            has_more=response["meta"]["has_more"],
            next_cursor=response["meta"].get("next_cursor"),
        )

    def get_metrics(self, window: MetricsWindow = "24h") -> Metrics:
        """
        Get aggregated delivery metrics.

        Args:
            window: Time window for aggregation (1h, 24h, 7d, 30d)

        Returns:
            Metrics with counts and success rate
        """
        response = self._request("GET", f"/v1/metrics?window={window}")
        data = response["data"]
        return Metrics(
            window=data["window"],
            total_messages=data["total_messages"],
            succeeded=data["succeeded"],
            failed=data["failed"],
            retries=data["retries"],
            success_rate=data["success_rate"],
            avg_latency_ms=data["avg_latency_ms"],
        )

    def get_dlq_messages(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> DLQMessagesResponse:
        """
        List messages in the Dead Letter Queue.

        Args:
            limit: Maximum results to return (1-1000, default 100)
            cursor: Pagination cursor from previous response

        Returns:
            DLQMessagesResponse with failed messages
        """
        params: dict[str, str] = {}
        if limit:
            params["limit"] = str(limit)
        if cursor:
            params["cursor"] = cursor

        path = "/v1/dlq/messages"
        if params:
            path = f"{path}?{urlencode(params)}"

        response = self._request("GET", path)
        data = response["data"]
        return DLQMessagesResponse(
            messages=[self._parse_message_summary(m) for m in (data.get("messages") or [])],
            has_more=data["has_more"],
            next_cursor=data.get("next_cursor"),
        )

    def replay_from_dlq(self, message_id: str) -> None:
        """
        Replay a message from the Dead Letter Queue.

        Args:
            message_id: The message ID to replay
        """
        self._request("POST", f"/v1/dlq/replay/{message_id}")

    def list_api_keys(self) -> list[APIKeyInfo]:
        """
        List all API keys for the project.

        Returns:
            List of APIKeyInfo
        """
        response = self._request("GET", "/v1/api-keys")
        return [
            APIKeyInfo(
                key_id=key["key_id"],
                label=key["label"],
                prefix=key["prefix"],
                created_at=self._parse_datetime(key["created_at"]),
                last_used_at=(
                    self._parse_datetime(key["last_used_at"]) if key.get("last_used_at") else None
                ),
            )
            for key in response["data"]
        ]

    def create_api_key(
        self,
        mode: APIKeyMode,
        *,
        label: Optional[str] = None,
    ) -> CreateAPIKeyResponse:
        """
        Create a new API key.

        Args:
            mode: Key mode ('live' or 'test')
            label: Optional human-readable label

        Returns:
            CreateAPIKeyResponse with the new key (shown only once!)
        """
        body: dict[str, Any] = {"mode": mode}
        if label:
            body["label"] = label

        response = self._request("POST", "/v1/api-keys", json=body)
        data = response["data"]
        return CreateAPIKeyResponse(
            key_id=data["key_id"],
            key=data["key"],
            prefix=data["prefix"],
            label=data["label"],
            created_at=self._parse_datetime(data["created_at"]),
        )

    def delete_api_key(self, key_id: str) -> None:
        """
        Delete an API key.

        Args:
            key_id: The API key ID to delete
        """
        self._request("DELETE", f"/v1/api-keys/{key_id}")

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retries."""
        last_error: Optional[Exception] = None

        for attempt in range(self._retries + 1):
            try:
                response = self._client.request(method, path, json=json)

                if not response.is_success:
                    self._handle_error_response(response)

                return response.json()  # type: ignore[no-any-return]

            except HookBridgeError as e:
                # Don't retry client errors (4xx)
                if e.status_code and 400 <= e.status_code < 500:
                    raise
                last_error = e

            except httpx.TimeoutException:
                last_error = TimeoutError()

            except httpx.RequestError as e:
                last_error = NetworkError(str(e))

            # Wait before retrying
            if attempt < self._retries:
                import time

                time.sleep(2**attempt * 0.1)

        if last_error:
            raise last_error
        raise NetworkError("Request failed")

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            data = response.json()
            code = data.get("error", {}).get("code", "UNKNOWN_ERROR")
            message = data.get("error", {}).get("message", f"HTTP {response.status_code}")
            request_id = data.get("meta", {}).get("request_id")
        except Exception:
            code = "UNKNOWN_ERROR"
            message = f"HTTP {response.status_code}"
            request_id = None

        if response.status_code == 401:
            raise AuthenticationError(message, request_id)
        elif response.status_code == 404:
            raise NotFoundError(message, request_id)
        elif response.status_code == 409:
            if code == "IDEMPOTENCY_MISMATCH":
                raise IdempotencyError(message, request_id)
            raise HookBridgeError(message, code, request_id, response.status_code)
        elif response.status_code == 429:
            if code == "REPLAY_LIMIT_EXCEEDED":
                raise ReplayLimitError(message, request_id)
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message, request_id, int(retry_after) if retry_after else None
            )
        else:
            raise HookBridgeError(message, code, request_id, response.status_code)

    def _parse_message(self, data: dict[str, Any]) -> Message:
        """Parse a message from API response."""
        return Message(
            id=data["id"],
            project_id=data["project_id"],
            endpoint_id=data["endpoint_id"],
            status=data["status"],
            attempt_count=data["attempt_count"],
            replay_count=data["replay_count"],
            content_type=data["content_type"],
            size_bytes=data["size_bytes"],
            payload_sha256=data["payload_sha256"],
            created_at=self._parse_datetime(data["created_at"]),
            updated_at=self._parse_datetime(data["updated_at"]),
            idempotency_key=data.get("idempotency_key"),
            next_attempt_at=(
                self._parse_datetime(data["next_attempt_at"])
                if data.get("next_attempt_at")
                else None
            ),
            last_error=data.get("last_error"),
            response_status=data.get("response_status"),
            response_latency_ms=data.get("response_latency_ms"),
        )

    def _parse_message_summary(self, data: dict[str, Any]) -> MessageSummary:
        """Parse a message summary from API response."""
        return MessageSummary(
            message_id=data["message_id"],
            endpoint=data["endpoint"],
            status=data["status"],
            attempt_count=data["attempt_count"],
            created_at=self._parse_datetime(data["created_at"]),
            delivered_at=(
                self._parse_datetime(data["delivered_at"]) if data.get("delivered_at") else None
            ),
            response_status=data.get("response_status"),
            response_latency_ms=data.get("response_latency_ms"),
            last_error=data.get("last_error"),
        )

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        """Parse an ISO 8601 datetime string."""
        # Handle both with and without microseconds
        if "." in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


class AsyncHookBridge:
    """
    HookBridge API client (asynchronous).

    Example:
        >>> from hookbridge import AsyncHookBridge
        >>>
        >>> async with AsyncHookBridge(api_key="hb_live_xxx") as client:
        ...     result = await client.send(
        ...         endpoint="https://customer.app/webhooks",
        ...         payload={"event": "order.created"}
        ...     )
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        """
        Create a new async HookBridge client.

        Args:
            api_key: Your HookBridge API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            retries: Number of retries for failed requests
        """
        if not api_key:
            raise ValidationError("API key is required")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "hookbridge-python/1.0.0",
            },
        )

    async def __aenter__(self) -> "AsyncHookBridge":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def send(
        self,
        endpoint: str,
        payload: dict[str, Any],
        *,
        headers: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SendWebhookResponse:
        """Send a webhook for delivery."""
        body = {
            "endpoint": endpoint,
            "payload": payload,
        }
        if headers:
            body["headers"] = headers
        if idempotency_key:
            body["idempotency_key"] = idempotency_key

        response = await self._request("POST", "/v1/webhooks/send", json=body)
        data = response["data"]

        return SendWebhookResponse(
            message_id=data["message_id"],
            status=data["status"],
        )

    async def get_message(self, message_id: str) -> Message:
        """Get details for a specific message."""
        response = await self._request("GET", f"/v1/messages/{message_id}")
        return self._parse_message(response["data"])

    async def replay(self, message_id: str) -> None:
        """Replay a message for redelivery."""
        await self._request("POST", f"/v1/messages/{message_id}/replay")

    async def cancel_retry(self, message_id: str) -> None:
        """Cancel a pending retry."""
        await self._request("POST", f"/v1/messages/{message_id}/cancel")

    async def retry_now(self, message_id: str) -> None:
        """Trigger an immediate retry for a pending message."""
        await self._request("POST", f"/v1/messages/{message_id}/retry-now")

    async def get_logs(
        self,
        *,
        status: Optional[MessageStatus] = None,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LogsResponse:
        """Query delivery logs with optional filters."""
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if start_time:
            params["start_time"] = (
                start_time.isoformat() if isinstance(start_time, datetime) else start_time
            )
        if end_time:
            params["end_time"] = (
                end_time.isoformat() if isinstance(end_time, datetime) else end_time
            )
        if limit:
            params["limit"] = str(limit)
        if cursor:
            params["cursor"] = cursor

        path = "/v1/logs"
        if params:
            path = f"{path}?{urlencode(params)}"

        response = await self._request("GET", path)
        return LogsResponse(
            messages=[self._parse_message_summary(m) for m in response["data"]],
            has_more=response["meta"]["has_more"],
            next_cursor=response["meta"].get("next_cursor"),
        )

    async def get_metrics(self, window: MetricsWindow = "24h") -> Metrics:
        """Get aggregated delivery metrics."""
        response = await self._request("GET", f"/v1/metrics?window={window}")
        data = response["data"]
        return Metrics(
            window=data["window"],
            total_messages=data["total_messages"],
            succeeded=data["succeeded"],
            failed=data["failed"],
            retries=data["retries"],
            success_rate=data["success_rate"],
            avg_latency_ms=data["avg_latency_ms"],
        )

    async def get_dlq_messages(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> DLQMessagesResponse:
        """List messages in the Dead Letter Queue."""
        params: dict[str, str] = {}
        if limit:
            params["limit"] = str(limit)
        if cursor:
            params["cursor"] = cursor

        path = "/v1/dlq/messages"
        if params:
            path = f"{path}?{urlencode(params)}"

        response = await self._request("GET", path)
        data = response["data"]
        return DLQMessagesResponse(
            messages=[self._parse_message_summary(m) for m in (data.get("messages") or [])],
            has_more=data["has_more"],
            next_cursor=data.get("next_cursor"),
        )

    async def replay_from_dlq(self, message_id: str) -> None:
        """Replay a message from the Dead Letter Queue."""
        await self._request("POST", f"/v1/dlq/replay/{message_id}")

    async def list_api_keys(self) -> list[APIKeyInfo]:
        """List all API keys for the project."""
        response = await self._request("GET", "/v1/api-keys")
        return [
            APIKeyInfo(
                key_id=key["key_id"],
                label=key["label"],
                prefix=key["prefix"],
                created_at=self._parse_datetime(key["created_at"]),
                last_used_at=(
                    self._parse_datetime(key["last_used_at"]) if key.get("last_used_at") else None
                ),
            )
            for key in response["data"]
        ]

    async def create_api_key(
        self,
        mode: APIKeyMode,
        *,
        label: Optional[str] = None,
    ) -> CreateAPIKeyResponse:
        """Create a new API key."""
        body: dict[str, Any] = {"mode": mode}
        if label:
            body["label"] = label

        response = await self._request("POST", "/v1/api-keys", json=body)
        data = response["data"]
        return CreateAPIKeyResponse(
            key_id=data["key_id"],
            key=data["key"],
            prefix=data["prefix"],
            label=data["label"],
            created_at=self._parse_datetime(data["created_at"]),
        )

    async def delete_api_key(self, key_id: str) -> None:
        """Delete an API key."""
        await self._request("DELETE", f"/v1/api-keys/{key_id}")

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retries."""
        import asyncio

        last_error: Optional[Exception] = None

        for attempt in range(self._retries + 1):
            try:
                response = await self._client.request(method, path, json=json)

                if not response.is_success:
                    self._handle_error_response(response)

                return response.json()  # type: ignore[no-any-return]

            except HookBridgeError as e:
                if e.status_code and 400 <= e.status_code < 500:
                    raise
                last_error = e

            except httpx.TimeoutException:
                last_error = TimeoutError()

            except httpx.RequestError as e:
                last_error = NetworkError(str(e))

            if attempt < self._retries:
                await asyncio.sleep(2**attempt * 0.1)

        if last_error:
            raise last_error
        raise NetworkError("Request failed")

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            data = response.json()
            code = data.get("error", {}).get("code", "UNKNOWN_ERROR")
            message = data.get("error", {}).get("message", f"HTTP {response.status_code}")
            request_id = data.get("meta", {}).get("request_id")
        except Exception:
            code = "UNKNOWN_ERROR"
            message = f"HTTP {response.status_code}"
            request_id = None

        if response.status_code == 401:
            raise AuthenticationError(message, request_id)
        elif response.status_code == 404:
            raise NotFoundError(message, request_id)
        elif response.status_code == 409:
            if code == "IDEMPOTENCY_MISMATCH":
                raise IdempotencyError(message, request_id)
            raise HookBridgeError(message, code, request_id, response.status_code)
        elif response.status_code == 429:
            if code == "REPLAY_LIMIT_EXCEEDED":
                raise ReplayLimitError(message, request_id)
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message, request_id, int(retry_after) if retry_after else None
            )
        else:
            raise HookBridgeError(message, code, request_id, response.status_code)

    def _parse_message(self, data: dict[str, Any]) -> Message:
        """Parse a message from API response."""
        return Message(
            id=data["id"],
            project_id=data["project_id"],
            endpoint_id=data["endpoint_id"],
            status=data["status"],
            attempt_count=data["attempt_count"],
            replay_count=data["replay_count"],
            content_type=data["content_type"],
            size_bytes=data["size_bytes"],
            payload_sha256=data["payload_sha256"],
            created_at=self._parse_datetime(data["created_at"]),
            updated_at=self._parse_datetime(data["updated_at"]),
            idempotency_key=data.get("idempotency_key"),
            next_attempt_at=(
                self._parse_datetime(data["next_attempt_at"])
                if data.get("next_attempt_at")
                else None
            ),
            last_error=data.get("last_error"),
            response_status=data.get("response_status"),
            response_latency_ms=data.get("response_latency_ms"),
        )

    def _parse_message_summary(self, data: dict[str, Any]) -> MessageSummary:
        """Parse a message summary from API response."""
        return MessageSummary(
            message_id=data["message_id"],
            endpoint=data["endpoint"],
            status=data["status"],
            attempt_count=data["attempt_count"],
            created_at=self._parse_datetime(data["created_at"]),
            delivered_at=(
                self._parse_datetime(data["delivered_at"]) if data.get("delivered_at") else None
            ),
            response_status=data.get("response_status"),
            response_latency_ms=data.get("response_latency_ms"),
            last_error=data.get("last_error"),
        )

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        """Parse an ISO 8601 datetime string."""
        if "." in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
