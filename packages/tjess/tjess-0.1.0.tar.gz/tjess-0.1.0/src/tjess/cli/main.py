"""TJESS CLI - Main entry point."""

import typer
from rich.console import Console

from tjess.cli import __version__
from tjess.cli.commands import agent, auth, init

app = typer.Typer(
    name="tjess",
    help="TJESS CLI - Build and deploy agents on the TJESS platform",
    no_args_is_help=True,
)

console = Console()

# Register command groups
app.add_typer(agent.app, name="agent", help="Agent development and deployment")
app.add_typer(auth.app, name="auth", help="Authentication management")
# Register init as a command, not a subgroup
app.command(name="init")(init.init)


@app.callback()
def main_callback():
    """TJESS CLI - Build and deploy agents on the TJESS platform."""
    pass


@app.command()
def version():
    """Show CLI version."""
    console.print(f"tjess version {__version__}")


if __name__ == "__main__":
    app()
