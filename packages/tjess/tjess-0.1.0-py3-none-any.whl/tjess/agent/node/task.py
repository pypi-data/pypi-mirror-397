"""Task Producer and Worker for async job queues."""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

from tjess.agent.node.message_queue import MessageQueue, ProcessingMode

logger = logging.getLogger(__name__)


class TaskProducer:
    """
    Producer for pushing tasks to a queue.

    Similar to ROS Action Client (but simpler, fire-and-forget).
    """

    def __init__(self, air_client, queue_name: str = "default"):
        """
        Args:
            air_client: AirClient instance
            queue_name: Queue name
        """
        self.air_client = air_client
        self.queue_name = queue_name
        self._is_active = True

    async def push(self, task: dict[str, Any]):
        """Push a task to the queue."""
        if not self._is_active:
            logger.warning(f"TaskProducer for {self.queue_name} is not active")
            return

        await self.air_client.push_task(task, queue=self.queue_name)

    def shutdown(self):
        """Mark producer as inactive."""
        self._is_active = False


class TaskWorker:
    """
    Worker for processing tasks from a queue.

    Supports two modes:
    - CALLBACK: Process tasks immediately with callback (default)
    - ENQUEUE: Buffer tasks for manual processing via spin_once()
    """

    def __init__(
        self,
        air_client,
        queue_name: str,
        callback: Callable[[dict[str, Any]], Awaitable[None]],
        processing_mode: ProcessingMode = ProcessingMode.CALLBACK,
        message_queue: Optional[MessageQueue] = None,
    ):
        """
        Args:
            air_client: AirClient instance
            queue_name: Queue name to listen to
            callback: Async callback function to process tasks
            processing_mode: CALLBACK or ENQUEUE
            message_queue: Shared message queue (required for ENQUEUE mode)
        """
        self.air_client = air_client
        self.queue_name = queue_name
        self.callback = callback
        self.processing_mode = processing_mode
        self.message_queue = message_queue
        self._task: Optional[asyncio.Task] = None
        self._is_active = False

        if processing_mode == ProcessingMode.ENQUEUE and message_queue is None:
            raise ValueError("message_queue required for ENQUEUE mode")

    async def start(self):
        """Start the task worker."""
        if self._is_active:
            logger.warning(f"TaskWorker for {self.queue_name} is already active")
            return

        self._is_active = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"TaskWorker started for queue: {self.queue_name} (mode: {self.processing_mode.value})")

    async def _run(self):
        """Internal run loop that processes tasks."""
        try:
            async for task in self.air_client.pull_tasks(queue=self.queue_name):
                if not self._is_active:
                    break

                if self.processing_mode == ProcessingMode.CALLBACK:
                    # Process immediately
                    try:
                        await self.callback(task)
                    except Exception as e:
                        logger.error(
                            f"Error in task worker callback for {self.queue_name}: {e}",
                            exc_info=True,
                        )
                else:
                    # Enqueue for manual processing
                    await self.message_queue.enqueue(
                        source_id=self.queue_name,
                        source_type="task",
                        message=task,
                        callback=self.callback,
                    )

        except asyncio.CancelledError:
            logger.info(f"TaskWorker for {self.queue_name} cancelled")
        except Exception as e:
            logger.error(f"TaskWorker error for {self.queue_name}: {e}", exc_info=True)
        finally:
            self._is_active = False

    async def shutdown(self):
        """Stop the task worker."""
        self._is_active = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"TaskWorker shutdown for queue: {self.queue_name}")
