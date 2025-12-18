"""Agent runner - connects to Air and executes agent handlers."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from typing import Any

import httpx
from pydantic_settings import BaseSettings

from tjess.agent.clients.air import AirClient
from tjess.agent.clients.identity import IdentityClient

logger = logging.getLogger(__name__)


class AgentConfig(BaseSettings):
    """Agent runtime configuration from environment variables."""

    # Air service URL
    air_url: str = "http://air:8000"

    # Identity service URL (for OAuth2 token exchange)
    identity_url: str = "http://identity:8000"

    # OAuth2 client credentials (exchanged for JWT)
    client_id: str = ""
    client_secret: str = ""

    # Legacy: direct token (prefer client credentials)
    auth_token: str = ""

    # Tenant ID (usually extracted from JWT, but can be set for local dev)
    tenant_id: str = "default"

    log_level: str = "INFO"

    class Config:
        env_prefix = "TJESS_"
        env_file = ".env"


class AgentRunner:
    """
    Agent runner that connects to Air and processes work.

    Supports multiple execution patterns:
    - Task worker: Pull tasks from a queue
    - RPC service: Handle request-reply
    - Event subscriber: React to events

    Authentication:
    - Prefers OAuth2 client credentials flow (TJESS_CLIENT_ID + TJESS_CLIENT_SECRET)
    - Falls back to direct token (TJESS_AUTH_TOKEN) for backwards compatibility
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
        version: str = "0.1.0",
        agent_type: str = "task_worker",
        tools: list[dict] | None = None,
    ):
        self.config = config or AgentConfig()
        self.agent_id = agent_id
        self.version = version
        self.agent_type = agent_type
        self.tools = tools or []
        self._shutdown = False
        self._tasks: list[asyncio.Task] = []
        self._queues: list[str] = []
        self._services: list[str] = []
        self._topics: list[str] = []
        self._registered = False
        self._heartbeat_task: asyncio.Task | None = None

        # Initialize clients
        self._identity = IdentityClient(
            base_url=self.config.identity_url,
            client_id=self.config.client_id or None,
            client_secret=self.config.client_secret or None,
        )
        self._air = AirClient(
            base_url=self.config.air_url,
            identity_client=self._identity,
        )

        # If legacy token is provided and no client credentials, set it directly
        if self.config.auth_token and not self.config.client_id:
            self._air.set_token(self.config.auth_token)

        # Setup logging
        logging.basicConfig(
            level=self.config.log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    async def _authenticate(self) -> None:
        """Authenticate with Identity service if credentials are configured."""
        if self.config.client_id and self.config.client_secret:
            try:
                await self._air.authenticate()
                logger.info("Authenticated with Identity service")
            except Exception as e:
                logger.warning(f"Failed to authenticate: {e}")
        elif self.config.auth_token:
            logger.debug("Using direct auth token (legacy mode)")
        else:
            logger.warning("No authentication configured")

    async def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for direct HTTP requests."""
        headers = {"Content-Type": "application/json"}
        if self._identity.client_id:
            token = await self._identity.get_token()
            headers["Authorization"] = f"Bearer {token}"
        elif self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        return headers

    async def _handle_shutdown(self):
        """Handle graceful shutdown."""
        self._shutdown = True

        # Stop heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        # Unregister from Air
        if self._registered and self.agent_id:
            await self._unregister()

        for task in self._tasks:
            task.cancel()
        logger.info("Shutting down agent...")

    async def _register(self) -> None:
        """Register agent with Air's discovery service."""
        if not self.agent_id:
            return

        url = f"{self.config.air_url}/agents/register"

        registration = {
            "agent_id": self.agent_id,
            "version": self.version,
            "type": self.agent_type,
            "tools": self.tools,
            "queues": self._queues,
            "services": self._services,
            "topics": self._topics,
        }

        try:
            headers = await self._get_auth_headers()
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=registration, headers=headers)
                response.raise_for_status()
                self._registered = True
                logger.info(f"Agent registered with Air: {self.agent_id}")
        except Exception as e:
            logger.warning(f"Failed to register with Air: {e}")

    async def _unregister(self) -> None:
        """Unregister agent from Air's discovery service."""
        if not self.agent_id:
            return

        url = f"{self.config.air_url}/agents/unregister"

        try:
            headers = await self._get_auth_headers()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json={"agent_id": self.agent_id}, headers=headers
                )
                response.raise_for_status()
                self._registered = False
                logger.info(f"Agent unregistered from Air: {self.agent_id}")
        except Exception as e:
            logger.warning(f"Failed to unregister from Air: {e}")

    async def _heartbeat_loop(self, interval: float = 30.0) -> None:
        """Send periodic heartbeats to Air."""
        if not self.agent_id:
            return

        url = f"{self.config.air_url}/agents/heartbeat"

        while not self._shutdown:
            try:
                await asyncio.sleep(interval)
                headers = await self._get_auth_headers()
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, json={"agent_id": self.agent_id}, headers=headers
                    )
                    response.raise_for_status()
                    logger.debug(f"Heartbeat sent for {self.agent_id}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")

    def _setup_signals(self):
        """Setup signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self._handle_shutdown()))

    async def run_task_worker(self, queue: str, handler) -> None:
        """
        Run as a task worker, pulling tasks from a queue.

        Args:
            queue: Queue name to pull tasks from
            handler: Async function to handle each task
        """
        # Track queue for registration
        if queue not in self._queues:
            self._queues.append(queue)

        logger.info(f"Starting task worker on queue: {queue}")

        while not self._shutdown:
            try:
                async for task_data in self._air.pull_tasks(queue=queue):
                    if self._shutdown:
                        break
                    try:
                        logger.debug(f"Received task: {task_data}")
                        result = await handler(task_data)
                        logger.debug(f"Task completed: {result}")
                    except Exception as e:
                        logger.exception(f"Error handling task: {e}")
            except Exception as e:
                if not self._shutdown:
                    logger.error(f"Task worker error: {e}")
                    await asyncio.sleep(5)

    async def run_rpc_service(self, service: str, handler) -> None:
        """
        Run as an RPC service, handling request-reply patterns.

        Args:
            service: Service name to register as
            handler: Async function to handle each request
        """
        # Track service for registration
        if service not in self._services:
            self._services.append(service)

        logger.info(f"Starting RPC service: {service}")

        while not self._shutdown:
            try:
                async for request in self._air.rpc_serve(service):
                    if self._shutdown:
                        break

                    request_id = request.get("request_id")
                    payload = request.get("payload", {})
                    tenant = request.get("tenant", "default")

                    logger.debug(f"RPC request {request_id}: {payload}")

                    try:
                        # Handle request
                        result = await handler(payload)

                        # Send response
                        await self._air.rpc_respond(
                            service,
                            request_id,
                            result,
                            tenant=tenant,
                        )
                        logger.debug(f"RPC response sent for {request_id}")
                    except Exception as e:
                        logger.exception(f"Error handling RPC: {e}")
                        try:
                            await self._air.rpc_respond(
                                service,
                                request_id,
                                {"error": str(e)},
                                tenant=tenant,
                            )
                        except Exception:
                            pass
            except Exception as e:
                if not self._shutdown:
                    logger.error(f"RPC service error: {e}")
                    await asyncio.sleep(5)

    async def run_event_subscriber(self, topic: str, handler) -> None:
        """
        Run as an event subscriber, reacting to events.

        Args:
            topic: Topic to subscribe to
            handler: Async function to handle each event
        """
        # Track topic for registration
        if topic not in self._topics:
            self._topics.append(topic)

        logger.info(f"Starting event subscriber on topic: {topic}")

        while not self._shutdown:
            try:
                async for event in self._air.subscribe_events(topic):
                    if self._shutdown:
                        break
                    try:
                        logger.debug(f"Received event: {event}")
                        await handler(event)
                    except Exception as e:
                        logger.exception(f"Error handling event: {e}")
            except Exception as e:
                if not self._shutdown:
                    logger.error(f"Event subscriber error: {e}")
                    await asyncio.sleep(5)

    async def publish_event(self, topic: str, message: dict[str, Any]) -> None:
        """Publish an event to a topic."""
        await self._air.publish_event(topic, message)

    async def send_task(self, queue: str, task: dict[str, Any]) -> None:
        """Send a task to a queue."""
        await self._air.push_task(task, queue=queue)

    async def call_rpc(
        self, service: str, payload: dict[str, Any], timeout: int = 5000
    ) -> dict[str, Any]:
        """Make an RPC call to a service."""
        return await self._air.rpc_request(service, payload, timeout_ms=timeout)

    def run(self, *coroutines) -> None:
        """
        Run the agent with the given coroutines.

        Example:
            runner.run(
                runner.run_task_worker("queue1", handler1),
                runner.run_event_subscriber("topic1", handler2),
            )
        """

        async def main():
            self._setup_signals()

            # Authenticate first
            await self._authenticate()

            # Register with Air (after a short delay to let coroutines populate queues/services/topics)
            await asyncio.sleep(0.1)
            await self._register()

            # Start heartbeat
            if self.agent_id:
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            self._tasks = [asyncio.create_task(coro) for coro in coroutines]
            try:
                await asyncio.gather(*self._tasks)
            except asyncio.CancelledError:
                pass

            # Ensure unregistration happens
            if self._registered and self.agent_id:
                await self._unregister()

            # Close clients
            await self._air.close()

            logger.info("Agent stopped")

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass
        sys.exit(0)
