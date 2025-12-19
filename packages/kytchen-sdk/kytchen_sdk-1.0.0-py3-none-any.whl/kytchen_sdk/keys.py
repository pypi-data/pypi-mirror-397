"""API key operations for Kytchen SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import KytchenClient


class ApiKey:
    """API Key object."""
    def __init__(
        self,
        id: str,
        name: str,
        prefix: str,
        created_at: str,
        last_used_at: str | None = None,
        expires_at: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.prefix = prefix
        self.created_at = created_at
        self.last_used_at = last_used_at
        self.expires_at = expires_at

    def __repr__(self) -> str:
        return f"<ApiKey id={self.id} name={self.name}>"


class Keys:
    """API key management operations."""

    def __init__(self, client: KytchenClient) -> None:
        self._client = client

    async def list(self) -> list[ApiKey]:
        """List all API keys.

        Returns:
            List of API keys
        """
        data = await self._client._request("GET", "/v1/api-keys")
        return [self._parse_key(k) for k in data.get("keys", [])]

    async def create(
        self,
        name: str,
        expires_in: int = 90,
    ) -> dict[str, Any]:
        """Create a new API key.

        Args:
            name: Key name/description
            expires_in: Days until expiration (0 for no expiration)

        Returns:
            Dictionary containing the new key details including the full secret key
        """
        payload = {
            "name": name,
            "expires_in": expires_in,
        }

        data = await self._client._request("POST", "/v1/api-keys", json=payload)
        # Return raw data because it contains the secret key which is not part of the ApiKey model
        return data

    async def revoke(self, key_id: str) -> None:
        """Revoke an API key.

        Args:
            key_id: The key ID to revoke
        """
        await self._client._request("DELETE", f"/v1/api-keys/{key_id}")

    def _parse_key(self, data: dict) -> ApiKey:
        """Parse API response into ApiKey object."""
        return ApiKey(
            id=data["id"],
            name=data["name"],
            prefix=data["prefix"],
            created_at=data["created_at"],
            last_used_at=data.get("last_used_at"),
            expires_at=data.get("expires_at"),
        )
