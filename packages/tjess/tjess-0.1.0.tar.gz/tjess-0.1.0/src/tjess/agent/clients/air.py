"""Air service client for messaging and communication."""

import json
import logging
from typing import Any, AsyncGenerator, Optional

import httpx

from tjess.agent.clients.identity import IdentityClient

logger = logging.getLogger(__name__)


class BearerAuth(httpx.Auth):
    """
    Custom authentication handler that automatically refreshes tokens.

    Uses IdentityClient for token management.
    """

    def __init__(self, identity_client: IdentityClient, scope: Optional[str] = None):
        self.identity_client = identity_client
        self.scope = scope
        self._token: Optional[str] = None

    async def async_auth_flow(self, request: httpx.Request):
        # Get a fresh token (IdentityClient handles caching internally)
        if self.identity_client.client_id:
            self._token = await self.identity_client.get_token(scope=self.scope)
            request.headers["Authorization"] = f"Bearer {self._token}"

        response = yield request

        # If we get a 401, try refreshing the token once
        if response.status_code == 401 and self.identity_client.client_id:
            logger.debug("Received 401, refreshing token")
            self._token = await self.identity_client._refresh_token(scope=self.scope)
            request.headers["Authorization"] = f"Bearer {self._token}"
            yield request


class AirClient:
    """
    Client for interacting with the Air service.

    Provides methods for:
    - Broadcasting messages (pub/sub)
    - Event publishing and subscribing (queued with tracking)
    - RPC request/response patterns
    - Task queue push/pull

    Automatically handles token refresh on expiration when configured
    with an IdentityClient.

    Example:
        identity = IdentityClient(client_id="my-agent", client_secret="secret")
        air = AirClient(base_url="http://air:8000", identity_client=identity)
        await air.authenticate()

        # Publish a message
        await air.publish_broadcast("sensors/temp", {"value": 22.5})

        # Subscribe to messages
        async for msg in air.subscribe_broadcast("sensors/temp"):
            print(msg)
    """

    def __init__(
        self,
        base_url: str = "http://air:8000",
        identity_client: Optional[IdentityClient] = None,
    ):
        """
        Initialize the Air client.

        Args:
            base_url: Air service URL
            identity_client: Optional IdentityClient for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.identity = identity_client or IdentityClient()
        self._auth = BearerAuth(self.identity)
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            auth=self._auth,
        )

    def set_token(self, token: str):
        """
        Manually set the Bearer token for requests.

        Note: Using authenticate() is preferred as it enables auto-refresh.
        """
        self._async_client.headers["Authorization"] = f"Bearer {token}"

    async def authenticate(self, scope: Optional[str] = None) -> str:
        """
        Authenticate using the internal IdentityClient.

        This enables automatic token refresh on subsequent requests.

        Args:
            scope: Optional OAuth scope

        Returns:
            The access token
        """
        self._auth.scope = scope
        token = await self.identity.get_token(scope=scope)
        return token

    # ==================== Broadcast (Pub/Sub) ====================

    async def publish_broadcast(self, topic: str, message: dict[str, Any]):
        """
        Publish a message to the broadcast system (fire-and-forget pub/sub).

        Args:
            topic: Topic name
            message: Message payload
        """
        try:
            response = await self._async_client.post(
                "/api/broadcast",
                params={"topic": topic},
                json=message,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Broadcast publish error: {e.response.text}")
            raise

    async def subscribe_broadcast(self, topic: str) -> AsyncGenerator[dict[str, Any], None]:
        """
        Subscribe to a broadcast topic via SSE.

        Args:
            topic: Topic to subscribe to

        Yields:
            Messages as dictionaries
        """
        async with self._async_client.stream(
            "GET", "/api/broadcast", params={"topic": topic}
        ) as response:
            try:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
            except httpx.HTTPStatusError as e:
                logger.error(f"Broadcast subscribe error: {e.response.text}")
                raise

    # ==================== Events (Queued with tracking) ====================

    async def publish_event(self, topic: str, message: dict[str, Any]):
        """
        Publish an event to a topic.

        Events use queue-based messaging with subscription tracking.

        Args:
            topic: Topic name
            message: Event payload
        """
        try:
            response = await self._async_client.post(
                "/api/events",
                params={"topic": topic},
                json=message,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Event publish error: {e.response.text}")
            raise

    async def subscribe_events(self, topic: str) -> AsyncGenerator[dict[str, Any], None]:
        """
        Subscribe to events via SSE.

        Args:
            topic: Topic to subscribe to

        Yields:
            Event messages as dictionaries
        """
        async with self._async_client.stream(
            "GET", "/api/events", params={"topic": topic}
        ) as response:
            try:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
            except httpx.HTTPStatusError as e:
                logger.error(f"Event subscribe error: {e.response.text}")
                raise

    # ==================== RPC (Request/Response) ====================

    async def rpc_request(
        self,
        service: str,
        payload: dict[str, Any],
        timeout_ms: int = 5000,
    ) -> Any:
        """
        Send an RPC request and wait for response.

        Args:
            service: Service name
            payload: Request payload
            timeout_ms: Timeout in milliseconds

        Returns:
            Response from the service
        """
        try:
            response = await self._async_client.post(
                "/api/rpc/request",
                params={"service": service, "timeout": timeout_ms},
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"RPC request error: {e.response.text}")
            raise

    async def rpc_serve(self, service: str) -> AsyncGenerator[dict[str, Any], None]:
        """
        Act as an RPC service worker, receiving incoming requests.

        Args:
            service: Service name to register as

        Yields:
            Request dictionaries with:
            - request_id: str - ID to use in rpc_respond()
            - payload: dict - The request data
            - tenant: str - The tenant ID
        """
        async with self._async_client.stream(
            "GET", "/api/rpc/serve", params={"service": service}
        ) as response:
            try:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
            except httpx.HTTPStatusError as e:
                logger.error(f"RPC serve error: {e.response.text}")
                raise

    async def rpc_respond(
        self,
        service: str,
        request_id: str,
        response_payload: dict[str, Any],
        tenant: str = "default",
    ):
        """
        Submit a response to a pending RPC request.

        Args:
            service: Service name
            request_id: Request ID from the serve stream
            response_payload: The response data
            tenant: Tenant ID
        """
        try:
            response = await self._async_client.post(
                "/api/rpc/respond",
                params={"service": service, "request_id": request_id, "tenant": tenant},
                json=response_payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"RPC respond error: {e.response.text}")
            raise

    # ==================== Tasks (Job Queue) ====================

    async def push_task(
        self,
        task_payload: dict[str, Any],
        queue: str = "default",
    ):
        """
        Push a task to a queue for asynchronous processing.

        Args:
            task_payload: Task data
            queue: Queue name
        """
        try:
            response = await self._async_client.post(
                "/api/tasks",
                params={"queue": queue},
                json=task_payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Task push error: {e.response.text}")
            raise

    async def pull_tasks(self, queue: str = "default") -> AsyncGenerator[dict[str, Any], None]:
        """
        Register as a worker and pull tasks from a queue via SSE.

        The worker is automatically registered on connection and
        unregistered on disconnect.

        Args:
            queue: Queue name to listen to

        Yields:
            Task payloads as dictionaries
        """
        async with self._async_client.stream(
            "GET", "/api/tasks", params={"queue": queue}
        ) as response:
            try:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
            except httpx.HTTPStatusError as e:
                logger.error(f"Task pull error: {e.response.text}")
                raise

    async def close(self):
        """Close the HTTP client."""
        await self._async_client.aclose()
        await self.identity.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
