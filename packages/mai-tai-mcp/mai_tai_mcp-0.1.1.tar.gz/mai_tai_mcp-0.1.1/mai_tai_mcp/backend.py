"""Backend client for communicating with mai-tai API."""

from typing import Any, Optional

import httpx

from .config import MaiTaiConfig


class MaiTaiBackendError(Exception):
    """Error from mai-tai backend."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Backend error ({status_code}): {detail}")


class MaiTaiBackend:
    """Synchronous client for mai-tai backend API.

    Uses synchronous httpx since MCP tools are called synchronously.
    """

    def __init__(self, config: MaiTaiConfig):
        """Initialize backend client with configuration."""
        self.config = config
        self._client: Optional[httpx.Client] = None
        self.project_id: Optional[str] = None
        self.project_name: Optional[str] = None

    def _get_client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.server_url.rstrip("/"),
                headers={"X-API-Key": self.config.api_key},
                timeout=30.0,
            )
        return self._client

    def connect(self) -> bool:
        """Verify connection and get project info."""
        try:
            client = self._get_client()
            response = client.get("/api/v1/mcp/auth/verify")
            response.raise_for_status()
            data = response.json()
            self.project_id = data["project_id"]
            self.project_name = data["project_name"]
            return True
        except httpx.HTTPStatusError as e:
            raise MaiTaiBackendError(e.response.status_code, e.response.text) from e
        except Exception as e:
            raise MaiTaiBackendError(0, str(e)) from e

    def list_channels(self) -> list[dict[str, Any]]:
        """List all channels in the project."""
        client = self._get_client()
        response = client.get("/api/v1/mcp/channels")
        response.raise_for_status()
        data = response.json()
        return data["channels"]

    def create_channel(self, name: str, channel_type: str = "chat") -> dict[str, Any]:
        """Create a new channel."""
        client = self._get_client()
        response = client.post(
            "/api/v1/mcp/channels",
            json={"name": name, "type": channel_type},
        )
        response.raise_for_status()
        return response.json()

    def get_channel(self, channel_id: str) -> dict[str, Any]:
        """Get a channel by ID."""
        client = self._get_client()
        response = client.get(f"/api/v1/mcp/channels/{channel_id}")
        response.raise_for_status()
        return response.json()

    def send_message(
        self,
        channel_id: str,
        content: str,
        sender_type: str = "agent",
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Send a message to a channel."""
        client = self._get_client()
        payload: dict[str, Any] = {
            "content": content,
            "sender_type": sender_type,
        }
        if metadata:
            payload["metadata"] = metadata

        response = client.post(
            f"/api/v1/mcp/channels/{channel_id}/messages",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_messages(
        self,
        channel_id: str,
        limit: int = 50,
        after: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get messages from a channel."""
        client = self._get_client()
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after

        response = client.get(
            f"/api/v1/mcp/channels/{channel_id}/messages",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the client."""
        if self._client:
            self._client.close()
            self._client = None


def create_backend(config: Optional[MaiTaiConfig] = None) -> MaiTaiBackend:
    """Create a mai-tai backend client instance.

    Args:
        config: Optional configuration. If not provided, loads from environment.

    Returns:
        Configured MaiTaiBackend instance
    """
    if config is None:
        from .config import get_config

        config = get_config()

    return MaiTaiBackend(config)

