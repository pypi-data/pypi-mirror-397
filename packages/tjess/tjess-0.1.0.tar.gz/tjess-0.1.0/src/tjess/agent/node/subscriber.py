"""Subscriber for receiving messages from topics."""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

from tjess.agent.node.message_queue import MessageQueue, ProcessingMode

logger = logging.getLogger(__name__)


class Subscriber:
    """
    Subscriber for receiving messages from a topic.

    Supports two modes:
    - CALLBACK: Process messages immediately with callback (default)
    - ENQUEUE: Buffer messages for manual processing via spin_once()
    """

    def __init__(
        self,
        air_client,
        topic: str,
        callback: Callable[[dict[str, Any]], Awaitable[None]],
        message_type: str = "broadcast",
        queue_size: int = 10,
        processing_mode: ProcessingMode = ProcessingMode.CALLBACK,
        message_queue: Optional[MessageQueue] = None,
    ):
        """
        Args:
            air_client: AirClient instance
            topic: Topic name
            callback: Async callback function to process messages
            message_type: "broadcast" or "event"
            queue_size: Internal queue size for buffering (CALLBACK mode only)
            processing_mode: CALLBACK or ENQUEUE
            message_queue: Shared message queue (required for ENQUEUE mode)
        """
        self.air_client = air_client
        self.topic = topic
        self.callback = callback
        self.message_type = message_type
        self.queue_size = queue_size
        self.processing_mode = processing_mode
        self.message_queue = message_queue
        self._task: Optional[asyncio.Task] = None
        self._is_active = False
        self._queue: Optional[asyncio.Queue] = None

        if processing_mode == ProcessingMode.ENQUEUE and message_queue is None:
            raise ValueError("message_queue required for ENQUEUE mode")

        if processing_mode == ProcessingMode.CALLBACK:
            self._queue = asyncio.Queue(maxsize=queue_size)

    async def start(self):
        """Start the subscriber."""
        if self._is_active:
            logger.warning(f"Subscriber for {self.topic} is already active")
            return

        self._is_active = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"Subscriber started for topic: {self.topic} (mode: {self.processing_mode.value})")

    async def _run(self):
        """Internal run loop that processes messages."""
        try:
            # Get the appropriate subscription generator
            if self.message_type == "broadcast":
                stream = self.air_client.subscribe_broadcast(self.topic)
            elif self.message_type == "event":
                stream = self.air_client.subscribe_events(self.topic)
            else:
                raise ValueError(f"Unknown message_type: {self.message_type}")

            async for message in stream:
                if not self._is_active:
                    break

                if self.processing_mode == ProcessingMode.CALLBACK:
                    # Process immediately in callback
                    try:
                        await self.callback(message)
                    except Exception as e:
                        logger.error(f"Error in subscriber callback for {self.topic}: {e}", exc_info=True)
                else:
                    # Enqueue for manual processing
                    await self.message_queue.enqueue(
                        source_id=self.topic,
                        source_type="subscriber",
                        message=message,
                        callback=self.callback,
                    )

        except asyncio.CancelledError:
            logger.info(f"Subscriber for {self.topic} cancelled")
        except Exception as e:
            logger.error(f"Subscriber error for {self.topic}: {e}", exc_info=True)
        finally:
            self._is_active = False

    async def shutdown(self):
        """Stop the subscriber."""
        self._is_active = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"Subscriber shutdown for topic: {self.topic}")
