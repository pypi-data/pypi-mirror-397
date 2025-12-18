"""Agent decorators for defining capabilities and handlers."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, TypeVar

from tjess.agent.manifest import ToolDefinition

F = TypeVar("F", bound=Callable[..., Any])


class HandlerRegistry:
    """Registry for agent handlers."""

    def __init__(self):
        self.tools: dict[str, tuple[ToolDefinition, Callable]] = {}
        self.task_handlers: dict[str, Callable] = {}
        self.event_handlers: dict[str, Callable] = {}
        self.rpc_handlers: dict[str, Callable] = {}

    def clear(self):
        """Clear all registered handlers."""
        self.tools.clear()
        self.task_handlers.clear()
        self.event_handlers.clear()
        self.rpc_handlers.clear()


# Global registry (populated by decorators)
_registry = HandlerRegistry()


def get_registry() -> HandlerRegistry:
    """Get the global handler registry."""
    return _registry


def _extract_schema_from_signature(func: Callable) -> dict[str, Any]:
    """Extract JSON Schema from function signature."""
    sig = inspect.signature(func)
    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        prop: dict[str, Any] = {}

        # Get type annotation
        if param.annotation != inspect.Parameter.empty:
            annotation = param.annotation
            if annotation == str:
                prop["type"] = "string"
            elif annotation == int:
                prop["type"] = "integer"
            elif annotation == float:
                prop["type"] = "number"
            elif annotation == bool:
                prop["type"] = "boolean"
            elif annotation == list:
                prop["type"] = "array"
            elif annotation == dict:
                prop["type"] = "object"
            else:
                prop["type"] = "string"  # Default fallback

        # Check if required
        if param.default == inspect.Parameter.empty:
            required.append(name)
        else:
            prop["default"] = param.default

        properties[name] = prop

    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required

    return schema


def tool(
    name: str | None = None,
    description: str | None = None,
    parameters: dict[str, Any] | None = None,
    async_: bool = False,
    timeout: int = 30,
) -> Callable[[F], F]:
    """
    Decorator to register a function as an agent tool.

    Tools are callable capabilities that can be exposed via MCP, ACA, or internal RPC.

    Example:
        @tool(name="generate_report", description="Generate a report")
        async def generate_report(date: str, format: str = "pdf"):
            return {"url": "..."}
    """

    def decorator(func: F) -> F:
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"Tool: {tool_name}"
        tool_params = parameters or _extract_schema_from_signature(func)

        tool_def = ToolDefinition(
            name=tool_name,
            description=tool_desc,
            parameters=tool_params,
            **{"async": async_},
            timeout=timeout,
        )

        _registry.tools[tool_name] = (tool_def, func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def task_worker(queue: str) -> Callable[[F], F]:
    """
    Decorator to register a function as a task worker handler.

    Task workers pull tasks from a queue and process them.

    Example:
        @task_worker(queue="reports")
        async def handle_report_task(task: dict):
            return process_task(task)
    """

    def decorator(func: F) -> F:
        _registry.task_handlers[queue] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def event_subscriber(topic: str) -> Callable[[F], F]:
    """
    Decorator to register a function as an event subscriber.

    Event subscribers react to events published on a topic.

    Example:
        @event_subscriber(topic="user.created")
        async def handle_user_created(event: dict):
            send_welcome_email(event["user_id"])
    """

    def decorator(func: F) -> F:
        _registry.event_handlers[topic] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def rpc_service(service: str) -> Callable[[F], F]:
    """
    Decorator to register a function as an RPC service handler.

    RPC services handle request-reply patterns.

    Example:
        @rpc_service(service="analyzer")
        async def handle_analysis_request(request: dict):
            return {"result": analyze(request)}
    """

    def decorator(func: F) -> F:
        _registry.rpc_handlers[service] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
