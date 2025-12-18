"""Identity service client for OAuth2 authentication."""

import logging
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class IdentityClient:
    """
    Client for interacting with the Identity Service.

    Supports client credentials flow for machine-to-machine authentication,
    OIDC discovery, and JWKS fetching.

    Example:
        client = IdentityClient(
            base_url="http://identity:8000",
            client_id="my-agent",
            client_secret="secret"
        )
        token = await client.get_token()
    """

    def __init__(
        self,
        base_url: str = "http://identity:8000",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize the Identity client.

        Args:
            base_url: Identity service URL
            client_id: OAuth2 client ID (for client credentials flow)
            client_secret: OAuth2 client secret
        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._async_client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

        # Token management
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._openid_config: Optional[dict[str, Any]] = None

    async def get_openid_configuration(self) -> dict[str, Any]:
        """Fetch the OpenID Connect discovery document."""
        if self._openid_config:
            return self._openid_config

        try:
            response = await self._async_client.get("/.well-known/openid-configuration")
            response.raise_for_status()
            self._openid_config = response.json()
            return self._openid_config
        except Exception as e:
            logger.error(f"Failed to fetch OpenID configuration: {e}")
            raise

    async def get_jwks(self) -> dict[str, Any]:
        """Fetch the JSON Web Key Set (JWKS)."""
        jwks_uri = "/.well-known/jwks.json"

        if self._openid_config and "jwks_uri" in self._openid_config:
            jwks_uri = self._openid_config["jwks_uri"]

        try:
            response = await self._async_client.get(jwks_uri)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise

    async def get_token(self, scope: Optional[str] = None) -> str:
        """
        Get an access token using client credentials flow.

        Automatically caches and refreshes tokens when expired.

        Args:
            scope: Optional OAuth2 scope

        Returns:
            Access token string
        """
        # Return cached token if still valid (with 10s buffer)
        if self._access_token and time.time() < self._token_expires_at - 10:
            return self._access_token

        return await self._refresh_token(scope)

    async def _refresh_token(self, scope: Optional[str] = None) -> str:
        """Refresh the access token."""
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required for client_credentials flow")

        # Determine token endpoint (try discovery first)
        token_endpoint = "/oauth/token"
        if not self._openid_config:
            try:
                await self.get_openid_configuration()
            except Exception:
                pass  # Fall back to default endpoint

        if self._openid_config and "token_endpoint" in self._openid_config:
            token_endpoint = self._openid_config["token_endpoint"]

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if scope:
            data["scope"] = scope

        try:
            response = await self._async_client.post(token_endpoint, data=data)
            response.raise_for_status()
            token_data = response.json()

            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in

            logger.debug(f"Token refreshed, expires in {expires_in}s")
            return self._access_token
        except Exception as e:
            logger.error(f"Failed to get token: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self._async_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
