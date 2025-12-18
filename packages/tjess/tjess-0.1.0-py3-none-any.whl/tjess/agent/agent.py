"""Main Agent class - high-level API for building agents."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable

from tjess.agent.decorators import (
    HandlerRegistry,
    event_subscriber,
    get_registry,
    rpc_service,
    task_worker,
    tool,
)
from tjess.agent.manifest import AgentManifest, AgentType, ToolDefinition
from tjess.agent.runner import AgentConfig, AgentRunner

logger = logging.getLogger(__name__)


class Agent:
    """
    High-level agent class with decorator-based handler registration.

    Example:
        agent = Agent(name="my-agent")

        @agent.tool(description="Generate a report")
        async def generate_report(date: str, format: str = "pdf"):
            return {"url": "..."}

        @agent.on_task(queue="reports")
        async def handle_task(task: dict):
            return process(task)

        if __name__ == "__main__":
            agent.run()
    """

    def __init__(
        self,
        name: str | None = None,
        manifest_path: str | Path | None = None,
        config: AgentConfig | None = None,
    ):
        # Load manifest if provided
        if manifest_path:
            self.manifest = AgentManifest.from_yaml(manifest_path)
        elif name:
            self.manifest = AgentManifest.default(name)
        else:
            # Try to load from default location
            default_path = Path("agent.yaml")
            if default_path.exists():
                self.manifest = AgentManifest.from_yaml(default_path)
            else:
                raise ValueError("Must provide name, manifest_path, or have agent.yaml in cwd")

        self.config = config or AgentConfig()
        self._registry = get_registry()
        # Runner will be created in run() after we know the registered handlers
        self._runner: AgentRunner | None = None

    @property
    def name(self) -> str:
        return self.manifest.name

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
        parameters: dict[str, Any] | None = None,
        async_: bool = False,
        timeout: int = 30,
    ) -> Callable:
        """
        Decorator to register a tool.

        Example:
            @agent.tool(description="Generate a report")
            async def generate_report(date: str):
                return {"url": "..."}
        """
        return tool(
            name=name,
            description=description,
            parameters=parameters,
            async_=async_,
            timeout=timeout,
        )

    def on_task(self, queue: str | None = None) -> Callable:
        """
        Decorator to register a task handler.

        Example:
            @agent.on_task(queue="reports")
            async def handle_task(task: dict):
                return process(task)
        """
        q = queue or self.manifest.triggers.queue or self.name
        return task_worker(q)

    def on_event(self, topic: str | None = None) -> Callable:
        """
        Decorator to register an event handler.

        Example:
            @agent.on_event(topic="user.created")
            async def handle_event(event: dict):
                send_email(event)
        """
        t = topic or self.manifest.triggers.topic
        if not t:
            raise ValueError("Topic must be specified either in decorator or manifest")
        return event_subscriber(t)

    def on_rpc(self, service: str | None = None) -> Callable:
        """
        Decorator to register an RPC handler.

        Example:
            @agent.on_rpc(service="analyzer")
            async def handle_rpc(request: dict):
                return {"result": analyze(request)}
        """
        s = service or self.manifest.triggers.service or self.name
        return rpc_service(s)

    def get_tools(self) -> list[ToolDefinition]:
        """Get all registered tools."""
        return [tool_def for tool_def, _ in self._registry.tools.values()]

    async def call_tool(self, name: str, **kwargs) -> Any:
        """Call a registered tool by name."""
        if name not in self._registry.tools:
            raise ValueError(f"Tool not found: {name}")
        _, handler = self._registry.tools[name]
        return await handler(**kwargs)

    @property
    def runner(self) -> AgentRunner:
        """Get or create the runner."""
        if self._runner is None:
            self._runner = self._create_runner()
        return self._runner

    def _create_runner(self) -> AgentRunner:
        """Create runner with agent metadata for registration."""
        # Determine agent type
        agent_type = self.manifest.type.value

        # Convert tools to dict format for registration
        tools = [
            {
                "name": tool_def.name,
                "description": tool_def.description,
                "parameters": tool_def.parameters,
            }
            for tool_def, _ in self._registry.tools.values()
        ]

        return AgentRunner(
            config=self.config,
            agent_id=self.name,
            version=self.manifest.version,
            agent_type=agent_type,
            tools=tools,
        )

    def _build_coroutines(self) -> list:
        """Build the list of coroutines to run based on registered handlers."""
        coroutines = []

        # Task workers
        for queue, handler in self._registry.task_handlers.items():
            coroutines.append(self.runner.run_task_worker(queue, handler))

        # Event subscribers
        for topic, handler in self._registry.event_handlers.items():
            coroutines.append(self.runner.run_event_subscriber(topic, handler))

        # RPC services
        for service, handler in self._registry.rpc_handlers.items():
            coroutines.append(self.runner.run_rpc_service(service, handler))

        # If we have tools but no explicit handlers, run as RPC service
        if self._registry.tools and not coroutines:
            async def tool_handler(request: dict) -> dict:
                tool_name = request.get("tool") or request.get("name")
                arguments = request.get("arguments", {})
                if not tool_name or tool_name not in self._registry.tools:
                    return {"error": f"Unknown tool: {tool_name}"}
                try:
                    result = await self.call_tool(tool_name, **arguments)
                    return {"result": result}
                except Exception as e:
                    return {"error": str(e)}

            service = self.manifest.triggers.service or self.name
            coroutines.append(self.runner.run_rpc_service(service, tool_handler))

        return coroutines

    def run(self) -> None:
        """
        Run the agent.

        This starts all registered handlers based on their type:
        - Task workers connect to their queues
        - Event subscribers connect to their topics
        - RPC services register and wait for requests
        - Tools are exposed via RPC if no other handlers are registered
        """
        coroutines = self._build_coroutines()

        if not coroutines:
            raise RuntimeError(
                "No handlers registered. Use @agent.on_task, @agent.on_event, "
                "@agent.on_rpc, or @agent.tool decorators to register handlers."
            )

        logger.info(f"Starting agent: {self.name}")
        logger.info(f"  Task queues: {list(self._registry.task_handlers.keys())}")
        logger.info(f"  Event topics: {list(self._registry.event_handlers.keys())}")
        logger.info(f"  RPC services: {list(self._registry.rpc_handlers.keys())}")
        logger.info(f"  Tools: {list(self._registry.tools.keys())}")

        self.runner.run(*coroutines)

    # Convenience methods for inter-agent communication

    async def publish(self, topic: str, message: dict[str, Any]) -> None:
        """Publish an event to a topic."""
        await self.runner.publish_event(topic, message)

    async def send(self, queue: str, task: dict[str, Any]) -> None:
        """Send a task to a queue."""
        await self.runner.send_task(queue, task)

    async def call(
        self, service: str, payload: dict[str, Any], timeout: int = 5000
    ) -> dict[str, Any]:
        """Make an RPC call to another service/agent."""
        return await self.runner.call_rpc(service, payload, timeout)
