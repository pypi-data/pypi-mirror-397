"""Initialize a new agent project."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(no_args_is_help=False)
console = Console()


MAIN_PY_TEMPLATE = '''"""Agent entry point."""

from tjess.agent import Agent

agent = Agent()


@agent.on_task(queue="{name}")
async def handle_task(task: dict):
    """Handle incoming tasks."""
    # Process the task
    result = {{"processed": True, "input": task}}
    return result


@agent.tool(description="Example tool that echoes input")
async def echo(message: str) -> dict:
    """Echo the input message back."""
    return {{"echo": message}}


if __name__ == "__main__":
    agent.run()
'''

AGENT_YAML_TEMPLATE = """name: {name}
version: 0.1.0
description: {description}

type: task_worker

triggers:
  queue: {name}

limits:
  cpu: 500m
  memory: 256Mi
  timeout: 300

env:
  LOG_LEVEL: INFO
"""

REQUIREMENTS_TEMPLATE = """tjess>=0.1.0
"""

GITIGNORE_TEMPLATE = """.env
__pycache__/
*.pyc
.tjess/
.venv/
"""

ENV_EXAMPLE_TEMPLATE = """# TJESS Agent Configuration
TJESS_AIR_URL=http://localhost:8000
TJESS_IDENTITY_URL=http://localhost:8001
TJESS_CLIENT_ID=
TJESS_CLIENT_SECRET=
TJESS_LOG_LEVEL=INFO
"""


@app.callback(invoke_without_command=True)
def init(
    name: str = typer.Argument(None, help="Agent name"),
    directory: Path = typer.Option(
        None, "--dir", "-d", help="Directory to create agent in"
    ),
    description: str = typer.Option(
        "", "--description", help="Agent description"
    ),
    template: str = typer.Option(
        "task_worker",
        "--template",
        "-t",
        help="Agent template (task_worker, rpc_service, event_subscriber)",
    ),
):
    """Initialize a new agent project."""
    # Use current directory name if no name provided
    if not name:
        name = typer.prompt("Agent name")

    # Determine target directory
    target_dir = directory or Path.cwd() / name

    if target_dir.exists() and any(target_dir.iterdir()):
        if not typer.confirm(f"Directory {target_dir} is not empty. Continue?"):
            raise typer.Exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold blue]Creating agent:[/bold blue] {name}")
    console.print(f"[dim]Directory: {target_dir}[/dim]\n")

    # Create files
    files_created = []

    # agent.yaml
    agent_yaml = target_dir / "agent.yaml"
    agent_yaml.write_text(
        AGENT_YAML_TEMPLATE.format(
            name=name,
            description=description or f"{name} agent",
        )
    )
    files_created.append("agent.yaml")

    # main.py
    main_py = target_dir / "main.py"
    main_py.write_text(MAIN_PY_TEMPLATE.format(name=name))
    files_created.append("main.py")

    # requirements.txt
    requirements = target_dir / "requirements.txt"
    requirements.write_text(REQUIREMENTS_TEMPLATE)
    files_created.append("requirements.txt")

    # .gitignore
    gitignore = target_dir / ".gitignore"
    gitignore.write_text(GITIGNORE_TEMPLATE)
    files_created.append(".gitignore")

    # .env.example
    env_example = target_dir / ".env.example"
    env_example.write_text(ENV_EXAMPLE_TEMPLATE)
    files_created.append(".env.example")

    # .tjess directory
    tjess_dir = target_dir / ".tjess"
    tjess_dir.mkdir(exist_ok=True)
    files_created.append(".tjess/")

    # Print summary
    console.print("[green]Created files:[/green]")
    for f in files_created:
        console.print(f"  [dim]•[/dim] {f}")

    console.print(
        Panel(
            f"""[bold]Next steps:[/bold]

1. [cyan]cd {name}[/cyan]
2. [cyan]pip install -r requirements.txt[/cyan]
3. [cyan]tjess agent run[/cyan]

[dim]Edit main.py to add your agent logic.[/dim]
[dim]Edit agent.yaml to configure triggers and resources.[/dim]""",
            title="✨ Agent created",
            border_style="green",
        )
    )
