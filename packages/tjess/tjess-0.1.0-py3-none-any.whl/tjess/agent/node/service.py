"""Service Client and Server for RPC communication."""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

from tjess.agent.node.message_queue import MessageQueue, ProcessingMode

logger = logging.getLogger(__name__)


class ServiceClient:
    """
    RPC Service Client for making synchronous request-reply calls.

    Similar to ROS ServiceClient.
    """

    def __init__(self, air_client, service_name: str, timeout_ms: int = 5000):
        """
        Args:
            air_client: AirClient instance
            service_name: Service name
            timeout_ms: Request timeout in milliseconds
        """
        self.air_client = air_client
        self.service_name = service_name
        self.timeout_ms = timeout_ms

    async def call(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Call the service and wait for response.

        Args:
            request: Request payload

        Returns:
            Response from the service
        """
        return await self.air_client.rpc_request(
            self.service_name,
            request,
            timeout_ms=self.timeout_ms,
        )


class ServiceServer:
    """
    RPC Service Server for handling incoming service requests.

    Supports two modes:
    - CALLBACK: Process requests immediately with callback (default)
    - ENQUEUE: Buffer requests for manual processing via spin_once()
    """

    def __init__(
        self,
        air_client,
        service_name: str,
        callback: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        processing_mode: ProcessingMode = ProcessingMode.CALLBACK,
        message_queue: Optional[MessageQueue] = None,
    ):
        """
        Args:
            air_client: AirClient instance
            service_name: Service name to register
            callback: Async callback that processes request and returns response
            processing_mode: CALLBACK or ENQUEUE
            message_queue: Shared message queue (required for ENQUEUE mode)
        """
        self.air_client = air_client
        self.service_name = service_name
        self.callback = callback
        self.processing_mode = processing_mode
        self.message_queue = message_queue
        self._task: Optional[asyncio.Task] = None
        self._is_active = False

        if processing_mode == ProcessingMode.ENQUEUE and message_queue is None:
            raise ValueError("message_queue required for ENQUEUE mode")

    async def start(self):
        """Start the service server."""
        if self._is_active:
            logger.warning(f"ServiceServer for {self.service_name} is already active")
            return

        self._is_active = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"ServiceServer started for: {self.service_name} (mode: {self.processing_mode.value})")

    async def _run(self):
        """Internal run loop that processes service requests."""
        try:
            async for request_data in self.air_client.rpc_serve(self.service_name):
                if not self._is_active:
                    break

                # Extract request information
                request_id = request_data.get("request_id")
                payload = request_data.get("payload", {})
                tenant = request_data.get("tenant", "default")

                if self.processing_mode == ProcessingMode.CALLBACK:
                    # Process immediately
                    try:
                        response = await self.callback(payload)
                        await self.air_client.rpc_respond(
                            self.service_name,
                            request_id,
                            response,
                            tenant=tenant,
                        )
                    except Exception as e:
                        logger.error(
                            f"Error processing service request for {self.service_name}: {e}",
                            exc_info=True,
                        )
                        try:
                            await self.air_client.rpc_respond(
                                self.service_name,
                                request_id,
                                {"error": str(e), "success": False},
                                tenant=tenant,
                            )
                        except Exception as respond_error:
                            logger.error(f"Failed to send error response: {respond_error}")
                else:
                    # Enqueue for manual processing
                    await self.message_queue.enqueue(
                        source_id=self.service_name,
                        source_type="service",
                        message=payload,
                        callback=self.callback,
                        request_context={
                            "request_id": request_id,
                            "tenant": tenant,
                            "service_name": self.service_name,
                        },
                    )

        except asyncio.CancelledError:
            logger.info(f"ServiceServer for {self.service_name} cancelled")
        except Exception as e:
            logger.error(f"ServiceServer error for {self.service_name}: {e}", exc_info=True)
        finally:
            self._is_active = False

    async def shutdown(self):
        """Stop the service server."""
        self._is_active = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"ServiceServer shutdown for: {self.service_name}")
