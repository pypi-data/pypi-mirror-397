"""Publisher for sending messages to topics."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Publisher:
    """
    Publisher for broadcasting or publishing messages to a topic.

    Similar to ROS Publisher.
    """

    def __init__(self, air_client, topic: str, message_type: str = "broadcast"):
        """
        Args:
            air_client: AirClient instance
            topic: Topic name
            message_type: "broadcast" or "event"
        """
        self.air_client = air_client
        self.topic = topic
        self.message_type = message_type
        self._is_active = True

    async def publish(self, message: dict[str, Any]):
        """Publish a message to the topic."""
        if not self._is_active:
            logger.warning(f"Publisher for {self.topic} is not active")
            return

        if self.message_type == "broadcast":
            await self.air_client.publish_broadcast(self.topic, message)
        elif self.message_type == "event":
            await self.air_client.publish_event(self.topic, message)
        else:
            raise ValueError(f"Unknown message_type: {self.message_type}")

    def shutdown(self):
        """Mark publisher as inactive."""
        self._is_active = False
