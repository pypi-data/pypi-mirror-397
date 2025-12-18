"""
TjessNode - ROS-like interface for the Tjess Platform.

Provides precise control over message processing for robotics-style
sense-compute-act loops.
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

from tjess.agent.clients.air import AirClient
from tjess.agent.clients.identity import IdentityClient
from tjess.agent.node.message_queue import MessageQueue, ProcessingMode
from tjess.agent.node.publisher import Publisher
from tjess.agent.node.rate import Rate
from tjess.agent.node.service import ServiceClient, ServiceServer
from tjess.agent.node.subscriber import Subscriber
from tjess.agent.node.task import TaskProducer, TaskWorker

logger = logging.getLogger("tjess.agent.node")


class TjessNode:
    """
    TjessNode provides a ROS-like interface to the Tjess Platform.

    The node manages Publishers, Subscribers, Service Clients/Servers, and Task Workers
    similar to how ROS nodes work.

    Key Feature: Manual Message Processing Control
    =============================================
    Set `enqueue=True` when creating subscribers/servers/workers to buffer messages
    for manual processing. Then use `spin_once()` to process them one at a time.

    This gives you precise control over execution order - perfect for sense-compute-act loops!

    ROS-like Interface:
        Publishers/Subscribers:
        - create_publisher(topic, message_type) -> Publisher
        - create_subscriber(topic, callback, enqueue=False) -> Subscriber

        Services:
        - create_service_client(service_name) -> ServiceClient
        - create_service_server(service_name, callback, enqueue=False) -> ServiceServer

        Tasks:
        - create_task_producer(queue_name) -> TaskProducer
        - create_task_worker(queue_name, callback, enqueue=False) -> TaskWorker

        Loop Control:
        - await node.spin() - Run forever (for callback mode)
        - await node.spin_once() - Process ONE queued message (for enqueue mode)
        - node.create_rate(hz) - Create rate limiter

    Example with enqueue=False (callback mode, default):
        async with TjessNode(...) as node:
            await node.authenticate()

            # Messages processed immediately in background
            async def callback(msg):
                print(msg)

            sub = node.create_subscriber("topic", callback)  # enqueue=False by default
            await sub.start()
            await node.spin()  # Run forever

    Example with enqueue=True (manual control):
        async with TjessNode(...) as node:
            await node.authenticate()

            # Messages buffered for manual processing
            async def callback(msg):
                print(msg)

            sub = node.create_subscriber("topic", callback, enqueue=True)
            await sub.start()

            rate = node.create_rate(10)  # 10 Hz
            while True:
                # 1. Process ONE message
                await node.spin_once()

                # 2. Do computation
                result = compute()

                # 3. Publish result
                await pub.publish(result)

                # 4. Maintain rate
                await rate.sleep()
    """

    def __init__(
        self,
        air_url: str = "http://air:8000",
        identity_url: str = "http://identity:8000",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        message_queue_size: int = 1000,
    ):
        """
        Initialize the TjessNode.

        Args:
            air_url: Base URL for the Air Service.
            identity_url: Base URL for the Identity Service.
            client_id: OAuth2 Client ID (optional).
            client_secret: OAuth2 Client Secret (optional).
            message_queue_size: Maximum size of the message queue for enqueue mode.
        """
        self.identity = IdentityClient(
            base_url=identity_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.air = AirClient(base_url=air_url, identity_client=self.identity)

        # Centralized message queue for enqueue mode
        self._message_queue = MessageQueue(max_size=message_queue_size)

        # Track managed resources for cleanup
        self._publishers: list[Publisher] = []
        self._subscribers: list[Subscriber] = []
        self._service_clients: list[ServiceClient] = []
        self._service_servers: list[ServiceServer] = []
        self._task_producers: list[TaskProducer] = []
        self._task_workers: list[TaskWorker] = []

        logger.info(f"Initialized TjessNode with Air [{air_url}] and Identity [{identity_url}]")

    async def authenticate(self, scope: Optional[str] = None) -> str:
        """
        Authenticate using IdentityClient credentials.

        Returns:
            The obtained access token.
        """
        if not self.identity.client_id:
            logger.warning("No client_id provided for IdentityClient. Cannot authenticate.")
            return ""

        token = await self.air.authenticate(scope=scope)
        logger.info("Authenticated successfully")
        return token

    # ==================== Publisher/Subscriber Pattern ====================

    def create_publisher(self, topic: str, message_type: str = "broadcast") -> Publisher:
        """
        Create a publisher for a topic.

        Args:
            topic: Topic name
            message_type: "broadcast" (pub/sub, no persistence) or "event" (queued with tracking)

        Returns:
            Publisher instance

        Example:
            pub = node.create_publisher("sensors/temperature", "broadcast")
            await pub.publish({"temp": 22.5, "unit": "C"})
        """
        publisher = Publisher(self.air, topic, message_type)
        self._publishers.append(publisher)
        logger.info(f"Created publisher for topic: {topic} (type: {message_type})")
        return publisher

    def create_subscriber(
        self,
        topic: str,
        callback: Callable[[dict[str, Any]], Awaitable[None]],
        message_type: str = "broadcast",
        enqueue: bool = False,
        queue_size: int = 10,
    ) -> Subscriber:
        """
        Create a subscriber for a topic.

        Args:
            topic: Topic name
            callback: Async function to process messages
            message_type: "broadcast" or "event"
            enqueue: If True, buffer messages for manual processing via spin_once()
                    If False (default), process messages immediately with callback
            queue_size: Internal queue size (only used when enqueue=False)

        Returns:
            Subscriber instance (must call .start() to begin receiving)

        Example (immediate processing):
            async def handle_temp(msg):
                print(f"Temperature: {msg['temp']}")

            sub = node.create_subscriber("sensors/temp", handle_temp)
            await sub.start()
            await node.spin()  # Run forever

        Example (manual control):
            async def handle_temp(msg):
                print(f"Temperature: {msg['temp']}")

            sub = node.create_subscriber("sensors/temp", handle_temp, enqueue=True)
            await sub.start()

            while True:
                await node.spin_once()  # Process one message
                # ... do other work ...
        """
        mode = ProcessingMode.ENQUEUE if enqueue else ProcessingMode.CALLBACK
        subscriber = Subscriber(
            self.air,
            topic,
            callback,
            message_type,
            queue_size,
            processing_mode=mode,
            message_queue=self._message_queue if enqueue else None,
        )
        self._subscribers.append(subscriber)
        logger.info(f"Created subscriber for topic: {topic} (type: {message_type}, enqueue: {enqueue})")
        return subscriber

    # ==================== Service Client/Server Pattern ====================

    def create_service_client(self, service_name: str, timeout_ms: int = 5000) -> ServiceClient:
        """
        Create an RPC service client.

        Args:
            service_name: Service name
            timeout_ms: Request timeout in milliseconds

        Returns:
            ServiceClient instance

        Example:
            client = node.create_service_client("calculator")
            result = await client.call({"op": "add", "a": 5, "b": 3})
        """
        client = ServiceClient(self.air, service_name, timeout_ms)
        self._service_clients.append(client)
        logger.info(f"Created service client for: {service_name}")
        return client

    def create_service_server(
        self,
        service_name: str,
        callback: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        enqueue: bool = False,
    ) -> ServiceServer:
        """
        Create an RPC service server.

        Args:
            service_name: Service name to register
            callback: Async function that processes request and returns response
            enqueue: If True, buffer requests for manual processing via spin_once()
                    If False (default), process requests immediately

        Returns:
            ServiceServer instance (must call .start() to begin serving)

        Example (immediate processing):
            async def handle_calc(req):
                return {"result": req["a"] + req["b"]}

            server = node.create_service_server("calculator", handle_calc)
            await server.start()
            await node.spin()

        Example (manual control):
            async def handle_calc(req):
                return {"result": req["a"] + req["b"]}

            server = node.create_service_server("calculator", handle_calc, enqueue=True)
            await server.start()

            while True:
                await node.spin_once()  # Process one request
                # ... do other work ...
        """
        mode = ProcessingMode.ENQUEUE if enqueue else ProcessingMode.CALLBACK
        server = ServiceServer(
            self.air,
            service_name,
            callback,
            processing_mode=mode,
            message_queue=self._message_queue if enqueue else None,
        )
        self._service_servers.append(server)
        logger.info(f"Created service server for: {service_name} (enqueue: {enqueue})")
        return server

    # ==================== Task Queue Pattern ====================

    def create_task_producer(self, queue_name: str = "default") -> TaskProducer:
        """
        Create a task producer for pushing tasks to a queue.

        Args:
            queue_name: Queue name

        Returns:
            TaskProducer instance

        Example:
            producer = node.create_task_producer("image_processing")
            await producer.push({"image_url": "...", "operation": "resize"})
        """
        producer = TaskProducer(self.air, queue_name)
        self._task_producers.append(producer)
        logger.info(f"Created task producer for queue: {queue_name}")
        return producer

    def create_task_worker(
        self,
        queue_name: str,
        callback: Callable[[dict[str, Any]], Awaitable[None]],
        enqueue: bool = False,
    ) -> TaskWorker:
        """
        Create a task worker for processing tasks from a queue.

        Args:
            queue_name: Queue name
            callback: Async function to process tasks
            enqueue: If True, buffer tasks for manual processing via spin_once()
                    If False (default), process tasks immediately

        Returns:
            TaskWorker instance (must call .start() to begin processing)

        Example (immediate processing):
            async def process_image(task):
                print(f"Processing: {task['image_url']}")

            worker = node.create_task_worker("image_processing", process_image)
            await worker.start()
            await node.spin()

        Example (manual control):
            async def process_image(task):
                print(f"Processing: {task['image_url']}")

            worker = node.create_task_worker("image_processing", process_image, enqueue=True)
            await worker.start()

            while True:
                await node.spin_once()  # Process one task
                # ... do other work ...
        """
        mode = ProcessingMode.ENQUEUE if enqueue else ProcessingMode.CALLBACK
        worker = TaskWorker(
            self.air,
            queue_name,
            callback,
            processing_mode=mode,
            message_queue=self._message_queue if enqueue else None,
        )
        self._task_workers.append(worker)
        logger.info(f"Created task worker for queue: {queue_name} (enqueue: {enqueue})")
        return worker

    # ==================== Lifecycle Management ====================

    async def spin(self):
        """
        Keep the node running indefinitely (similar to rclpy.spin()).

        Use this when you have subscribers/servers/workers in CALLBACK mode
        that process messages in the background.

        Example:
            async with TjessNode(...) as node:
                sub = node.create_subscriber("topic", callback)  # callback mode
                await sub.start()
                await node.spin()  # Run forever
        """
        try:
            await asyncio.Event().wait()  # Wait forever
        except asyncio.CancelledError:
            logger.info("Node spin cancelled")

    async def spin_once(self, timeout: float = 0.0) -> bool:
        """
        Process ONE queued message (similar to ROS spinOnce).

        This processes one message from subscribers/servers/workers that were
        created with enqueue=True, then returns control to your code.

        Perfect for sense-compute-act loops!

        Args:
            timeout: How long to wait for a message (seconds)
                    0 = non-blocking (return immediately if no message)
                    >0 = wait up to timeout seconds
                    None = wait forever (not recommended)

        Returns:
            True if a message was processed, False if no message available

        Example:
            rate = node.create_rate(10)  # 10 Hz
            while True:
                # 1. Process one message
                await node.spin_once(timeout=0.01)

                # 2. Do computation
                result = compute_something()

                # 3. Publish result
                await pub.publish(result)

                # 4. Maintain rate
                await rate.sleep()
        """
        queued_msg = await self._message_queue.get_message(timeout=timeout)

        if queued_msg is None:
            return False

        # Process the message
        try:
            if queued_msg.source_type == "subscriber":
                # Subscriber message - just invoke callback
                if queued_msg.callback:
                    await queued_msg.callback(queued_msg.message)

            elif queued_msg.source_type == "service":
                # Service request - invoke callback and send response
                if queued_msg.callback and queued_msg.request_context:
                    try:
                        response = await queued_msg.callback(queued_msg.message)
                        await self.air.rpc_respond(
                            queued_msg.request_context["service_name"],
                            queued_msg.request_context["request_id"],
                            response,
                            tenant=queued_msg.request_context["tenant"],
                        )
                    except Exception as e:
                        logger.error(f"Error processing service request: {e}", exc_info=True)
                        await self.air.rpc_respond(
                            queued_msg.request_context["service_name"],
                            queued_msg.request_context["request_id"],
                            {"error": str(e), "success": False},
                            tenant=queued_msg.request_context["tenant"],
                        )

            elif queued_msg.source_type == "task":
                # Task - just invoke callback
                if queued_msg.callback:
                    await queued_msg.callback(queued_msg.message)

            return True

        except Exception as e:
            logger.error(f"Error processing queued message from {queued_msg.source_id}: {e}", exc_info=True)
            return False

    def has_queued_messages(self) -> bool:
        """
        Check if there are messages waiting in the queue.

        Useful to check before calling spin_once().
        """
        return self._message_queue.has_messages()

    def queue_size(self) -> int:
        """Get the number of messages currently in the queue."""
        return self._message_queue.queue_size()

    def create_rate(self, hz: float) -> Rate:
        """
        Create a Rate object for controlling loop frequency (similar to rospy.Rate).

        Args:
            hz: Desired frequency in Hz

        Returns:
            Rate object

        Example:
            rate = node.create_rate(10)  # 10 Hz
            while True:
                await node.spin_once()
                # ... do work ...
                await rate.sleep()
        """
        return Rate(hz)

    async def close(self):
        """Close all managed resources and clients."""
        logger.info("Shutting down TjessNode...")

        # Shutdown all managed resources
        for pub in self._publishers:
            pub.shutdown()

        for sub in self._subscribers:
            await sub.shutdown()

        for server in self._service_servers:
            await server.shutdown()

        for producer in self._task_producers:
            producer.shutdown()

        for worker in self._task_workers:
            await worker.shutdown()

        # Close underlying clients
        await self.air.close()

        logger.info("TjessNode shutdown complete")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
