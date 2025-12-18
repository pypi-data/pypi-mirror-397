"""CLI configuration management."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class CLIConfig(BaseSettings):
    """CLI configuration loaded from environment and config file."""

    # API settings
    api_url: str = Field(default="https://api.tjess.com", description="Platform API URL")
    air_url: str = Field(default="https://api.tjess.com/api/air", description="Air service URL")
    identity_url: str = Field(default="https://api.tjess.com/api/identity", description="Identity service URL")

    # Authentication (legacy direct token)
    auth_token: str = Field(default="", description="Authentication token")
    tenant_id: str = Field(default="default", description="Tenant ID")

    # Local development
    local_air_url: str = Field(default="http://localhost:8000", description="Local Air URL")
    local_identity_url: str = Field(default="http://localhost:8001", description="Local Identity URL")

    class Config:
        env_prefix = "TJESS_"
        env_file = ".env"


class ProjectConfig(BaseModel):
    """Project-level configuration stored in .tjess/config.json."""

    api_url: str | None = None
    tenant_id: str | None = None
    default_env: str = "local"


def get_config_dir() -> Path:
    """Get the user's config directory (~/.tjess)."""
    config_dir = Path.home() / ".tjess"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_project_config_dir() -> Path | None:
    """Get project config directory if in a project."""
    cwd = Path.cwd()
    project_dir = cwd / ".tjess"
    if project_dir.exists():
        return project_dir
    return None


def load_config() -> CLIConfig:
    """Load CLI configuration from all sources."""
    return CLIConfig()


def load_project_config() -> ProjectConfig | None:
    """Load project-level configuration."""
    project_dir = get_project_config_dir()
    if not project_dir:
        return None

    config_file = project_dir / "config.json"
    if not config_file.exists():
        return ProjectConfig()

    with open(config_file) as f:
        data = json.load(f)
    return ProjectConfig.model_validate(data)


def save_project_config(config: ProjectConfig) -> None:
    """Save project-level configuration."""
    project_dir = Path.cwd() / ".tjess"
    project_dir.mkdir(exist_ok=True)

    config_file = project_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump(config.model_dump(exclude_none=True), f, indent=2)


# =============================================================================
# Authentication Storage
# =============================================================================


def _get_credentials_file() -> Path:
    """Get path to credentials file."""
    return get_config_dir() / "credentials.json"


def load_auth_data() -> dict[str, Any] | None:
    """Load stored authentication data."""
    creds_file = _get_credentials_file()
    if not creds_file.exists():
        return None

    try:
        with open(creds_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _save_auth_data(data: dict[str, Any]) -> None:
    """Save authentication data."""
    creds_file = _get_credentials_file()

    # Load existing data to preserve other fields
    existing = load_auth_data() or {}
    existing.update(data)

    with open(creds_file, "w") as f:
        json.dump(existing, f, indent=2)

    # Set restrictive permissions
    creds_file.chmod(0o600)


def save_auth_token(
    access_token: str,
    refresh_token: str | None = None,
    expires_in: int = 3600,
) -> None:
    """Save access token and metadata."""
    data = {
        "access_token": access_token,
        "expires_at": time.time() + expires_in if access_token else 0,
    }
    if refresh_token:
        data["refresh_token"] = refresh_token

    _save_auth_data(data)


def save_client_credentials(client_id: str, client_secret: str) -> None:
    """Save OAuth2 client credentials for automatic token refresh."""
    _save_auth_data({
        "client_id": client_id,
        "client_secret": client_secret,
    })


def load_client_credentials() -> dict[str, str] | None:
    """Load stored client credentials."""
    data = load_auth_data()
    if data and data.get("client_id") and data.get("client_secret"):
        return {
            "client_id": data["client_id"],
            "client_secret": data["client_secret"],
        }
    return None


def get_auth_token() -> str | None:
    """
    Get a valid access token, refreshing if necessary.

    Returns the token if valid, or None if not authenticated.
    """
    # Check environment variable first (legacy support)
    config = load_config()
    if config.auth_token:
        return config.auth_token

    # Check stored token
    auth_data = load_auth_data()
    if not auth_data:
        return None

    access_token = auth_data.get("access_token")
    expires_at = auth_data.get("expires_at", 0)

    # If token is still valid (with 60s buffer), return it
    if access_token and expires_at > time.time() + 60:
        return access_token

    # Try to refresh using stored credentials
    creds = load_client_credentials()
    if not creds:
        return None

    # Lazy import to avoid circular deps
    import httpx

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
                return token_data["access_token"]
    except Exception:
        pass

    return None
