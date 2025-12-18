"""TJESS Agent SDK - Build and deploy agents on the TJESS platform.

This SDK provides two programming patterns for building agents:

1. **Agent** (Decorator-based) - Serverless-style agents
   Simple decorators for defining handlers. Best for microservices and background workers.

   Example:
       from tjess.agent import Agent

       agent = Agent(name="my-agent")

       @agent.on_task(queue="tasks")
       async def handle(task):
           return process(task)

       agent.run()

2. **TjessNode** (ROS-like) - Real-time control agents
   Precise control over message processing. Best for robotics and control loops.

   Example:
       from tjess.agent import TjessNode

       async with TjessNode(client_id="agent", client_secret="secret") as node:
           await node.authenticate()
           sub = node.create_subscriber("sensors/temp", callback, enqueue=True)
           await sub.start()

           rate = node.create_rate(10)  # 10 Hz
           while True:
               await node.spin_once()  # Process one message
               await rate.sleep()
"""

# High-level Agent API (decorator-based)
from tjess.agent.agent import Agent
from tjess.agent.decorators import event_subscriber, rpc_service, task_worker, tool
from tjess.agent.manifest import AgentManifest, ToolDefinition
from tjess.agent.manifest import TriggerConfig as ManifestTriggerConfig
from tjess.agent.runner import AgentConfig, AgentRunner

# ROS-like TjessNode API
from tjess.agent.node import (
    MessageQueue,
    ProcessingMode,
    Publisher,
    QueuedMessage,
    Rate,
    ServiceClient,
    ServiceServer,
    Subscriber,
    TaskProducer,
    TaskWorker,
    TjessNode,
)

# Low-level clients
from tjess.agent.clients import AirClient, IdentityClient

__all__ = [
    # High-level Agent API
    "Agent",
    "AgentRunner",
    "AgentConfig",
    "AgentManifest",
    "ToolDefinition",
    "ManifestTriggerConfig",
    "tool",
    "task_worker",
    "event_subscriber",
    "rpc_service",
    # ROS-like TjessNode API
    "TjessNode",
    "Publisher",
    "Subscriber",
    "ServiceClient",
    "ServiceServer",
    "TaskProducer",
    "TaskWorker",
    "Rate",
    "MessageQueue",
    "ProcessingMode",
    "QueuedMessage",
    # Low-level clients
    "AirClient",
    "IdentityClient",
]
