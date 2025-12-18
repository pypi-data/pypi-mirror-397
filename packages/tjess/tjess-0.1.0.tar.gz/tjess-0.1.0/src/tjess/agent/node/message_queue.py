"""Message queue system for manual message processing control."""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Message processing mode."""

    CALLBACK = "callback"  # Process immediately with callback
    ENQUEUE = "enqueue"  # Enqueue for manual processing


@dataclass
class QueuedMessage:
    """A message in the processing queue."""

    source_id: str  # Identifier for the source (topic, service, queue name)
    source_type: str  # Type: "subscriber", "service", "task"
    message: dict[str, Any]
    callback: Optional[Callable[[dict[str, Any]], Awaitable[Any]]] = None
    request_context: Optional[dict[str, Any]] = None  # For services: request_id, tenant, etc.


class MessageQueue:
    """
    Centralized message queue for manual processing control.

    All receiving abstractions (subscribers, service servers, task workers)
    can enqueue messages here for processing during spin_once().

    This enables precise control over execution order - perfect for
    sense-compute-act loops in robotics applications.
    """

    def __init__(self, max_size: int = 1000):
        """
        Args:
            max_size: Maximum queue size (oldest dropped if full)
        """
        self._queue: asyncio.Queue[QueuedMessage] = asyncio.Queue(maxsize=max_size)
        self._max_size = max_size

    async def enqueue(
        self,
        source_id: str,
        source_type: str,
        message: dict[str, Any],
        callback: Optional[Callable[[dict[str, Any]], Awaitable[Any]]] = None,
        request_context: Optional[dict[str, Any]] = None,
    ):
        """
        Enqueue a message for processing.

        Args:
            source_id: Identifier (topic name, service name, queue name)
            source_type: Type of source
            message: The message data
            callback: Optional callback to invoke during processing
            request_context: Additional context (for services, tasks)
        """
        queued_msg = QueuedMessage(
            source_id=source_id,
            source_type=source_type,
            message=message,
            callback=callback,
            request_context=request_context,
        )

        try:
            self._queue.put_nowait(queued_msg)
        except asyncio.QueueFull:
            # Drop oldest message
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(queued_msg)
                logger.warning(f"Queue full, dropped oldest message from {source_id}")
            except Exception as e:
                logger.error(f"Error managing queue: {e}")

    async def get_message(self, timeout: Optional[float] = None) -> Optional[QueuedMessage]:
        """
        Get one message from the queue.

        Args:
            timeout: Timeout in seconds (None = block forever, 0 = non-blocking)

        Returns:
            QueuedMessage or None if timeout/empty
        """
        try:
            if timeout == 0:
                return self._queue.get_nowait()
            elif timeout is None:
                return await self._queue.get()
            else:
                return await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except (asyncio.QueueEmpty, asyncio.TimeoutError):
            return None

    def get_message_nowait(self) -> Optional[QueuedMessage]:
        """Get one message without blocking."""
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def has_messages(self) -> bool:
        """Check if there are messages waiting."""
        return not self._queue.empty()

    def queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()

    async def get_all_messages(self) -> list[QueuedMessage]:
        """Get all currently queued messages."""
        messages = []
        while not self._queue.empty():
            try:
                messages.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return messages
