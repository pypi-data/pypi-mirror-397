"""Agent manifest definitions - protocol-agnostic capability declarations."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Agent execution type."""

    TASK_WORKER = "task_worker"
    RPC_SERVICE = "rpc_service"
    EVENT_SUBSCRIBER = "event_subscriber"
    CRON = "cron"


class ToolDefinition(BaseModel):
    """Tool/capability definition - compatible with MCP and ACA."""

    name: str = Field(..., description="Tool name (used for routing)")
    description: str = Field(..., description="Human-readable description")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for parameters"
    )
    # Internal extensions
    async_: bool = Field(default=False, alias="async", description="Fire-and-forget mode")
    timeout: int = Field(default=30, description="Timeout in seconds")


class ResourceDefinition(BaseModel):
    """Resource definition - for MCP resources."""

    name: str = Field(..., description="Resource URI pattern")
    description: str = Field(..., description="Human-readable description")
    mime_type: str = Field(default="application/json", description="Content type")


class TriggerConfig(BaseModel):
    """Agent trigger configuration."""

    queue: str | None = Field(default=None, description="Task queue name")
    topic: str | None = Field(default=None, description="Event topic to subscribe")
    service: str | None = Field(default=None, description="RPC service name")
    schedule: str | None = Field(default=None, description="Cron schedule expression")


class ResourceLimits(BaseModel):
    """Resource limits for agent execution."""

    cpu: str = Field(default="500m", description="CPU limit")
    memory: str = Field(default="256Mi", description="Memory limit")
    timeout: int = Field(default=300, description="Max execution time in seconds")


class AgentManifest(BaseModel):
    """Agent manifest - the agent.yaml specification."""

    name: str = Field(..., description="Agent name (unique within tenant)")
    version: str = Field(default="0.1.0", description="Semantic version")
    description: str = Field(default="", description="Agent description")
    type: AgentType = Field(default=AgentType.TASK_WORKER, description="Execution type")

    # Capabilities (for protocol adapters)
    tools: list[ToolDefinition] = Field(default_factory=list)
    resources: list[ResourceDefinition] = Field(default_factory=list)

    # Triggers
    triggers: TriggerConfig = Field(default_factory=TriggerConfig)

    # Execution settings
    limits: ResourceLimits = Field(default_factory=ResourceLimits)
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")

    # Entry point
    entrypoint: str = Field(default="main:agent", description="Module:attribute path")

    @classmethod
    def from_yaml(cls, path: str | Path) -> AgentManifest:
        """Load manifest from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        """Save manifest to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.model_dump(exclude_none=True, by_alias=True), f, sort_keys=False)

    @classmethod
    def default(cls, name: str) -> AgentManifest:
        """Create a default manifest for a new agent."""
        return cls(
            name=name,
            version="0.1.0",
            description=f"{name} agent",
            type=AgentType.TASK_WORKER,
            triggers=TriggerConfig(queue=name),
        )
