# TJESS

Build, deploy, and run agents on the TJESS platform.

## Installation

```bash
pip install tjess
# or
uv add tjess
```

## Quick Start

### CLI

```bash
# Authenticate with client credentials
tjess auth login --client-id my-agent --client-secret secret123

# Create a new agent project
tjess init my-agent

# Run the agent locally
cd my-agent
tjess agent run

# Deploy to the platform
tjess agent deploy
```

### SDK

The SDK provides two programming patterns for building agents:

#### 1. Agent (Decorator-based) - Serverless-style

Simple decorators for defining handlers. Best for microservices and background workers.

```python
from tjess import Agent

agent = Agent(name="my-agent")

@agent.on_task(queue="tasks")
async def handle_task(task: dict):
    # Process the task
    return {"result": "done"}

@agent.tool(description="Generate a report")
async def generate_report(date: str, format: str = "pdf"):
    return {"url": f"https://reports/{date}.{format}"}

if __name__ == "__main__":
    agent.run()
```

#### 2. TjessNode (ROS-like) - Real-time control

Precise control over message processing. Best for robotics and control loops.

```python
import asyncio
from tjess import TjessNode

async def main():
    async with TjessNode(
        air_url="http://air:8000",
        identity_url="http://identity:8000",
        client_id="my-agent",
        client_secret="secret",
    ) as node:
        await node.authenticate()

        # Create subscriber with manual processing
        async def handle_sensor(msg):
            print(f"Temperature: {msg['temp']}")

        sub = node.create_subscriber("sensors/temp", handle_sensor, enqueue=True)
        await sub.start()

        # Create publisher
        pub = node.create_publisher("actuators/motor")

        # Control loop at 10 Hz
        rate = node.create_rate(10)
        while True:
            await node.spin_once()  # Process one message
            await pub.publish({"speed": 100})
            await rate.sleep()

asyncio.run(main())
```

## CLI Reference

### Authentication

```bash
# Login with client credentials (interactive)
tjess auth login

# Login with credentials as arguments
tjess auth login --client-id my-agent --client-secret secret123

# Check authentication status
tjess auth status

# Get current access token (for scripts)
tjess auth token

# Refresh token
tjess auth refresh

# Logout
tjess auth logout
```

### Agent Management

```bash
# Create new agent project
tjess init my-agent

# Run agent locally
tjess agent run

# Deploy agent to platform
tjess agent deploy

# List deployed agents
tjess agent list

# Show agent status
tjess agent status my-agent

# Show agent versions
tjess agent versions my-agent

# Rollback to previous version
tjess agent rollback my-agent 0.1.0

# Start/stop agent
tjess agent start my-agent
tjess agent stop my-agent

# Stream agent logs
tjess agent logs my-agent --follow
```

## Configuration

### Environment Variables

```bash
# Platform URLs
TJESS_API_URL=https://api.tjess.com
TJESS_AIR_URL=https://api.tjess.com/api/air
TJESS_IDENTITY_URL=https://api.tjess.com/api/identity

# OAuth2 client credentials
TJESS_CLIENT_ID=my-agent
TJESS_CLIENT_SECRET=secret

# Local development
TJESS_LOCAL_AIR_URL=http://localhost:8000
TJESS_LOCAL_IDENTITY_URL=http://localhost:8001

# Logging
TJESS_LOG_LEVEL=INFO
```

### agent.yaml

```yaml
name: my-agent
version: 0.1.0
description: My agent

type: task_worker

triggers:
  queue: my-agent

limits:
  cpu: 500m
  memory: 256Mi
  timeout: 300

env:
  LOG_LEVEL: INFO
```

## SDK API Reference

### Agent API

- `Agent(name, manifest_path, config)` - Create a new agent
- `@agent.on_task(queue)` - Register a task handler
- `@agent.on_event(topic)` - Register an event handler
- `@agent.on_rpc(service)` - Register an RPC handler
- `@agent.tool(name, description)` - Register a tool
- `agent.run()` - Start the agent

### TjessNode API

- `TjessNode(air_url, identity_url, client_id, client_secret)` - Create a node
- `node.authenticate()` - Authenticate with Identity service
- `node.create_publisher(topic)` - Create a publisher
- `node.create_subscriber(topic, callback, enqueue)` - Create a subscriber
- `node.create_service_client(service)` - Create an RPC client
- `node.create_service_server(service, callback)` - Create an RPC server
- `node.create_task_producer(queue)` - Create a task producer
- `node.create_task_worker(queue, callback)` - Create a task worker
- `node.spin()` - Run forever (callback mode)
- `node.spin_once(timeout)` - Process one message (enqueue mode)
- `node.create_rate(hz)` - Create a rate limiter

### Low-level Clients

- `AirClient` - HTTP client for Air service
- `IdentityClient` - OAuth2 client for Identity service

## License

MIT
