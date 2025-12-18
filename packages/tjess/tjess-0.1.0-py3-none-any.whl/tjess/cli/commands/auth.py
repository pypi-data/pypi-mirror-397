"""Authentication commands."""

import time

import httpx
import typer
from rich.console import Console

from tjess.cli.config import (
    get_auth_token,
    load_config,
    save_auth_token,
    save_client_credentials,
    load_client_credentials,
    load_auth_data,
)

app = typer.Typer()
console = Console()


@app.command()
def login(
    client_id: str = typer.Option(None, "--client-id", "-c", help="OAuth2 Client ID"),
    client_secret: str = typer.Option(None, "--client-secret", "-s", help="OAuth2 Client Secret"),
):
    """
    Authenticate with the TJESS platform using client credentials.

    Example:
        tjess auth login --client-id my-agent --client-secret secret123

    Or interactively:
        tjess auth login
    """
    if not client_id:
        client_id = typer.prompt("Client ID")
    if not client_secret:
        client_secret = typer.prompt("Client Secret", hide_input=True)

    config = load_config()

    console.print("\n[dim]Authenticating...[/dim]")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{config.identity_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

            if response.status_code == 200:
                token_data = response.json()

                # Save credentials for future use
                save_client_credentials(client_id, client_secret)

                # Save token
                save_auth_token(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in", 3600),
                )

                console.print("[green]✓ Successfully authenticated![/green]")
                console.print(f"[dim]Token expires in {token_data.get('expires_in', 3600) // 60} minutes[/dim]")
            elif response.status_code == 401:
                console.print("[red]Invalid client credentials[/red]")
                raise typer.Exit(1)
            else:
                console.print(f"[red]Authentication failed: {response.text}[/red]")
                raise typer.Exit(1)

    except httpx.ConnectError:
        console.print("[red]Could not connect to Identity service[/red]")
        console.print(f"[dim]URL: {config.identity_url}[/dim]")
        raise typer.Exit(1)


@app.command()
def refresh():
    """
    Refresh the access token using stored client credentials.

    This is automatically done when tokens expire, but can be run manually.
    """
    creds = load_client_credentials()
    if not creds:
        console.print("[red]No client credentials stored.[/red]")
        console.print("[dim]Run 'tjess auth login' first.[/dim]")
        raise typer.Exit(1)

    config = load_config()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{config.identity_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": creds["client_id"],
                    "client_secret": creds["client_secret"],
                },
            )

            if response.status_code == 200:
                token_data = response.json()
                save_auth_token(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in", 3600),
                )
                console.print("[green]✓ Token refreshed[/green]")
            else:
                console.print(f"[red]Failed to refresh token: {response.text}[/red]")
                raise typer.Exit(1)

    except httpx.ConnectError:
        console.print("[red]Could not connect to Identity service[/red]")
        raise typer.Exit(1)


@app.command()
def token():
    """
    Print the current access token.

    Useful for piping to other commands:
        curl -H "Authorization: Bearer $(tjess auth token)" ...
    """
    # Try to get existing token
    auth_data = load_auth_data()

    if auth_data and auth_data.get("access_token"):
        expires_at = auth_data.get("expires_at", 0)

        # If token is still valid (with 60s buffer), use it
        if expires_at > time.time() + 60:
            print(auth_data["access_token"])
            return

    # Token expired or missing, try to refresh
    creds = load_client_credentials()
    if not creds:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]", err=True)
        raise typer.Exit(1)

    config = load_config()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{config.identity_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": creds["client_id"],
                    "client_secret": creds["client_secret"],
                },
            )

            if response.status_code == 200:
                token_data = response.json()
                save_auth_token(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in", 3600),
                )
                print(token_data["access_token"])
            else:
                console.print(f"[red]Failed to get token: {response.text}[/red]", err=True)
                raise typer.Exit(1)

    except httpx.ConnectError:
        console.print("[red]Could not connect to Identity service[/red]", err=True)
        raise typer.Exit(1)


@app.command()
def logout():
    """Log out and clear stored credentials."""
    save_auth_token(access_token="")
    console.print("[green]✓ Logged out[/green]")
    console.print("[dim]Client credentials are preserved. Use 'tjess auth login' to get a new token.[/dim]")


@app.command()
def status():
    """Show authentication status."""
    auth_data = load_auth_data()
    config = load_config()
    creds = load_client_credentials()

    console.print("\n[bold]Authentication Status[/bold]\n")

    # Check client credentials
    if creds:
        console.print(f"[green]✓ Client credentials: Configured[/green]")
        console.print(f"  Client ID: {creds['client_id']}")
    else:
        console.print("[dim]○ Client credentials: Not configured[/dim]")
        console.print("[dim]  Run 'tjess auth login' to authenticate[/dim]")

    # Check token
    if auth_data and auth_data.get("access_token"):
        token = auth_data["access_token"]
        masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
        expires_at = auth_data.get("expires_at", 0)

        if expires_at > time.time():
            remaining = int(expires_at - time.time())
            console.print(f"[green]✓ Access token: Valid[/green]")
            console.print(f"  Token: {masked}")
            console.print(f"  Expires in: {remaining // 60} minutes")
        else:
            console.print("[yellow]⚠ Access token: Expired[/yellow]")
            if creds:
                console.print("[dim]  Run 'tjess auth refresh' to get a new token[/dim]")
    else:
        console.print("[dim]○ Access token: None[/dim]")

    console.print(f"\n[dim]Identity URL: {config.identity_url}[/dim]")
    console.print(f"[dim]API URL: {config.api_url}[/dim]")


@app.command()
def whoami():
    """Show current user/client information."""
    token = get_auth_token()
    if not token:
        console.print("[red]Not authenticated. Run 'tjess auth login' first.[/red]")
        raise typer.Exit(1)

    config = load_config()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{config.identity_url}/oauth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                info = response.json()
                console.print(f"\n[bold]Client Information[/bold]\n")
                if info.get("sub"):
                    console.print(f"  Subject: {info['sub']}")
                if info.get("client_id"):
                    console.print(f"  Client ID: {info['client_id']}")
                if info.get("org_id"):
                    console.print(f"  Organization: {info['org_id']}")
                if info.get("scope"):
                    console.print(f"  Scopes: {info['scope']}")
            elif response.status_code == 401:
                console.print("[red]Token expired. Run 'tjess auth refresh'.[/red]")
                raise typer.Exit(1)
            else:
                console.print(f"[red]Failed to fetch info: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[red]Could not connect to Identity service[/red]")
        raise typer.Exit(1)
