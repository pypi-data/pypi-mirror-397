"""
TJESS - Build, deploy, and run agents on the TJESS platform.

This package provides:
- Agent SDK for building agents (tjess.agent)
- CLI for deploying and managing agents (tjess.cli)

Quick Start:

    from tjess.agent import Agent

    agent = Agent(name="my-agent")

    @agent.on_task(queue="tasks")
    async def handle(task):
        return {"result": "done"}

    agent.run()
"""

__version__ = "0.1.0"

# Re-export main components for convenience
from tjess.agent import (
    Agent,
    AgentRunner,
    TjessNode,
    AirClient,
    IdentityClient,
)

__all__ = [
    "__version__",
    "Agent",
    "AgentRunner",
    "TjessNode",
    "AirClient",
    "IdentityClient",
]
