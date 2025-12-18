"""Agent development and deployment commands."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import httpx
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from tjess.cli.config import get_auth_token, load_config

app = typer.Typer()
console = Console()


def load_manifest(path: Path | None = None) -> dict:
    """Load agent.yaml manifest."""
    manifest_path = path or Path.cwd() / "agent.yaml"
    if not manifest_path.exists():
        console.print("[red]Error: agent.yaml not found[/red]")
        console.print("[dim]Run 'tjess init' to create a new agent project[/dim]")
        raise typer.Exit(1)

    with open(manifest_path) as f:
        return yaml.safe_load(f)


def get_api_client() -> httpx.Client:
    """Get configured API client."""
    config = load_config()
    headers = {"Content-Type": "application/json"}

    token = get_auth_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return httpx.Client(base_url=config.api_url, headers=headers, timeout=30)


@app.command()
def run(
    manifest: Path = typer.Option(None, "--manifest", "-m", help="Path to agent.yaml"),
    local: bool = typer.Option(True, "--local/--cloud", help="Run locally or in cloud"),
    env_file: Path = typer.Option(None, "--env", "-e", help="Environment file"),
):
    """Run the agent locally."""
    manifest_data = load_manifest(manifest)
    agent_name = manifest_data.get("name", "agent")

    console.print(f"\n[bold blue]Running agent:[/bold blue] {agent_name}")

    # Load environment
    if env_file and env_file.exists():
        console.print(f"[dim]Loading environment from {env_file}[/dim]")
        # Load .env file
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    # Set Air URL based on local/cloud
    config = load_config()
    if local:
        os.environ.setdefault("TJESS_AIR_URL", config.local_air_url)
    else:
        os.environ.setdefault("TJESS_AIR_URL", config.air_url)
        token = get_auth_token()
        if token:
            os.environ.setdefault("TJESS_AUTH_TOKEN", token)

    console.print(f"[dim]Air URL: {os.environ.get('TJESS_AIR_URL')}[/dim]\n")

    # Find and run the agent
    entrypoint = manifest_data.get("entrypoint", "main:agent")
    module_name, attr_name = entrypoint.split(":")

    # Add current directory to path
    sys.path.insert(0, str(Path.cwd()))

    try:
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the agent instance
            agent = getattr(module, attr_name)

            console.print("[green]Starting agent...[/green]\n")
            agent.run()
    except FileNotFoundError:
        console.print(f"[red]Error: Could not find {module_name}.py[/red]")
        raise typer.Exit(1)
    except AttributeError:
        console.print(f"[red]Error: Could not find '{attr_name}' in {module_name}.py[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Agent stopped[/yellow]")


@app.command()
def deploy(
    manifest: Path = typer.Option(None, "--manifest", "-m", help="Path to agent.yaml"),
    version: str = typer.Option(None, "--version", "-v", help="Version to deploy"),
    env: str = typer.Option("default", "--env", "-e", help="Environment (default, staging, prod)"),
):
    """Deploy the agent to the platform."""
    manifest_data = load_manifest(manifest)
    agent_name = manifest_data.get("name")
    deploy_version = version or manifest_data.get("version", "0.1.0")

    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold blue]Deploying agent:[/bold blue] {agent_name} v{deploy_version}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Package agent
        task = progress.add_task("Packaging agent...", total=None)

        # Create zip archive of agent code
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
                agent_dir = Path.cwd()
                for file in agent_dir.rglob("*"):
                    if file.is_file():
                        # Skip hidden dirs, __pycache__, .venv, etc.
                        rel_path = file.relative_to(agent_dir)
                        parts = rel_path.parts
                        if any(
                            p.startswith(".") or p == "__pycache__" or p == ".venv"
                            for p in parts
                        ):
                            continue
                        zf.write(file, rel_path)

            archive_path = tmp.name

        progress.update(task, description="Uploading to platform...")

        # Upload to API
        config = load_config()
        try:
            with open(archive_path, "rb") as f:
                files = {"code": (f"{agent_name}.zip", f, "application/zip")}
                data = {
                    "name": agent_name,
                    "version": deploy_version,
                    "config": json.dumps(manifest_data),
                }

                with httpx.Client(timeout=60) as client:
                    response = client.post(
                        f"{config.api_url}/api/runtime/agents",
                        files=files,
                        data=data,
                        headers={"Authorization": f"Bearer {token}"},
                    )

                    if response.status_code == 201:
                        progress.update(task, description="[green]Deployed![/green]")
                    elif response.status_code == 401:
                        console.print("\n[red]Authentication failed. Run 'tjess auth login'.[/red]")
                        raise typer.Exit(1)
                    else:
                        console.print(f"\n[red]Deploy failed: {response.text}[/red]")
                        raise typer.Exit(1)

        except httpx.ConnectError:
            console.print("\n[red]Could not connect to platform API[/red]")
            raise typer.Exit(1)
        finally:
            # Cleanup temp file
            Path(archive_path).unlink(missing_ok=True)

    console.print(
        Panel(
            f"""[green]✓ Agent deployed successfully[/green]

[bold]Name:[/bold] {agent_name}
[bold]Version:[/bold] {deploy_version}
[bold]Environment:[/bold] {env}

[dim]View status: tjess agent status {agent_name}[/dim]""",
            border_style="green",
        )
    )


@app.command("list")
def list_agents():
    """List deployed agents."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{config.api_url}/api/runtime/agents",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                agents = response.json()

                if not agents:
                    console.print("[dim]No agents deployed[/dim]")
                    return

                table = Table(title="Deployed Agents")
                table.add_column("Name", style="cyan")
                table.add_column("Version")
                table.add_column("Type")
                table.add_column("Status")

                for agent in agents:
                    status_color = "green" if agent.get("status") == "running" else "yellow"
                    table.add_row(
                        agent.get("name", ""),
                        agent.get("version", ""),
                        agent.get("type", ""),
                        f"[{status_color}]{agent.get('status', 'unknown')}[/{status_color}]",
                    )

                console.print(table)
            elif response.status_code == 401:
                console.print("[red]Authentication failed. Run 'tjess auth login'.[/red]")
                raise typer.Exit(1)
            else:
                console.print(f"[red]Failed to fetch agents: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    name: str = typer.Argument(..., help="Agent name"),
):
    """Show agent status and details."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{config.api_url}/api/runtime/agents/{name}",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                agent = response.json()

                status_color = "green" if agent.get("status") == "running" else "yellow"

                console.print(f"\n[bold]{agent.get('name')}[/bold]")
                console.print(f"  Version: {agent.get('version')}")
                console.print(f"  Type: {agent.get('type')}")
                console.print(f"  Status: [{status_color}]{agent.get('status')}[/{status_color}]")

                if agent.get("triggers"):
                    console.print(f"  Triggers: {agent.get('triggers')}")

                if agent.get("instances"):
                    console.print(f"  Running instances: {agent.get('instances')}")

            elif response.status_code == 404:
                console.print(f"[red]Agent '{name}' not found[/red]")
            elif response.status_code == 401:
                console.print("[red]Authentication failed[/red]")
                raise typer.Exit(1)

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
        raise typer.Exit(1)


@app.command()
def versions(
    name: str = typer.Argument(..., help="Agent name"),
):
    """List agent versions."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{config.api_url}/api/runtime/agents/{name}/versions",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                versions_list = response.json()

                table = Table(title=f"Versions: {name}")
                table.add_column("Version", style="cyan")
                table.add_column("Created")
                table.add_column("Current", justify="center")

                for v in versions_list:
                    current = "✓" if v.get("current") else ""
                    table.add_row(
                        v.get("version", ""),
                        v.get("created_at", "")[:19],
                        f"[green]{current}[/green]",
                    )

                console.print(table)
            elif response.status_code == 404:
                console.print(f"[red]Agent '{name}' not found[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
        raise typer.Exit(1)


@app.command()
def rollback(
    name: str = typer.Argument(..., help="Agent name"),
    version: str = typer.Argument(..., help="Version to rollback to"),
):
    """Rollback agent to a previous version."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    console.print(f"Rolling back {name} to version {version}...")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{config.api_url}/api/runtime/agents/{name}/rollback",
                json={"version": version},
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                console.print(f"[green]✓ Rolled back to version {version}[/green]")
            elif response.status_code == 404:
                console.print("[red]Agent or version not found[/red]")
            else:
                console.print(f"[red]Rollback failed: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
        raise typer.Exit(1)


@app.command()
def logs(
    name: str = typer.Argument(..., help="Agent name"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    lines: int = typer.Option(100, "--lines", "-n", help="Number of lines to show"),
):
    """Stream agent logs."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    console.print(f"[dim]Fetching logs for {name}...[/dim]\n")

    try:
        with httpx.Client(timeout=None) as client:
            params = {"lines": lines, "follow": follow}
            response = client.get(
                f"{config.api_url}/api/runtime/agents/{name}/logs",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    console.print(line)
            elif response.status_code == 404:
                console.print(f"[red]Agent '{name}' not found[/red]")
            else:
                console.print(f"[red]Failed to fetch logs: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
    except KeyboardInterrupt:
        pass


@app.command()
def stop(
    name: str = typer.Argument(..., help="Agent name"),
):
    """Stop a running agent."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    console.print(f"Stopping agent {name}...")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{config.api_url}/api/runtime/agents/{name}/stop",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                console.print(f"[green]✓ Agent {name} stopped[/green]")
            elif response.status_code == 404:
                console.print(f"[red]Agent '{name}' not found[/red]")
            else:
                console.print(f"[red]Failed to stop agent: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
        raise typer.Exit(1)


@app.command()
def start(
    name: str = typer.Argument(..., help="Agent name"),
):
    """Start a stopped agent."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    console.print(f"Starting agent {name}...")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{config.api_url}/api/runtime/agents/{name}/start",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                console.print(f"[green]✓ Agent {name} started[/green]")
            elif response.status_code == 404:
                console.print(f"[red]Agent '{name}' not found[/red]")
            else:
                console.print(f"[red]Failed to start agent: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to platform API[/red]")
        raise typer.Exit(1)
