"""HTTP client for Notifer API."""
import requests
from typing import Any, Optional
from .config import Config


class NotiferClient:
    """HTTP client for Notifer API."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize client with configuration."""
        self.config = config or Config.load()
        self.session = requests.Session()
        self._setup_auth()

    def _setup_auth(self):
        """Setup authentication headers."""
        if self.config.api_key:
            self.session.headers["X-API-Key"] = self.config.api_key
        elif self.config.access_token:
            self.session.headers["Authorization"] = f"Bearer {self.config.access_token}"

    def publish(
        self,
        topic: str,
        message: str,
        title: Optional[str] = None,
        priority: int = 3,
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Publish a message to a topic.

        Args:
            topic: Topic name
            message: Message content
            title: Optional message title
            priority: Priority (1-5, default: 3)
            tags: Optional list of tags

        Returns:
            Published message data

        Raises:
            requests.HTTPError: On API error
        """
        url = f"{self.config.server}/{topic}"
        payload = {
            "message": message,
            "priority": priority,
        }
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def subscribe(self, topic: str, since: Optional[str] = None):
        """
        Subscribe to a topic via SSE.

        Args:
            topic: Topic name
            since: Optional timestamp to get messages since

        Yields:
            Message events as they arrive
        """
        url = f"{self.config.server}/{topic}/sse"
        params = {}
        if since:
            params["since"] = since

        response = self.session.get(url, params=params, stream=True)
        response.raise_for_status()

        # Simple SSE parsing
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                import json
                data = line[6:]  # Remove "data: " prefix
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue

    # API Keys
    def list_api_keys(self) -> list[dict[str, Any]]:
        """List all API keys."""
        url = f"{self.config.server}/api/keys"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["keys"]

    def create_api_key(
        self,
        name: str,
        description: Optional[str] = None,
        scopes: Optional[list[str]] = None,
        expires_at: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new API key."""
        url = f"{self.config.server}/api/keys"
        payload = {"name": name}
        if description:
            payload["description"] = description
        if scopes:
            payload["scopes"] = scopes
        if expires_at:
            payload["expires_at"] = expires_at

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def revoke_api_key(self, key_id: str) -> dict[str, Any]:
        """Revoke an API key."""
        url = f"{self.config.server}/api/keys/{key_id}/revoke"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

    def delete_api_key(self, key_id: str):
        """Delete an API key."""
        url = f"{self.config.server}/api/keys/{key_id}"
        response = self.session.delete(url)
        response.raise_for_status()

    # Topics
    def list_topics(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """List all topics."""
        url = f"{self.config.server}/api/topics"
        params = {"limit": limit, "offset": offset}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def my_topics(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """List user's topics."""
        url = f"{self.config.server}/api/topics/my"
        params = {"limit": limit, "offset": offset}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_topic(self, name: str) -> dict[str, Any]:
        """Get topic details."""
        url = f"{self.config.server}/api/topics/{name}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def create_topic(
        self,
        name: str,
        description: Optional[str] = None,
        is_private: bool = False,
        is_discoverable: bool = True,
    ) -> dict[str, Any]:
        """Create a new topic."""
        url = f"{self.config.server}/api/topics"
        payload = {
            "name": name,
            "access_level": "private" if is_private else "public",
            "is_discoverable": is_discoverable,
        }
        if description:
            payload["description"] = description

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_topic(self, topic_id: str):
        """Delete a topic."""
        url = f"{self.config.server}/api/topics/{topic_id}"
        response = self.session.delete(url)
        response.raise_for_status()

    # Auth
    def login(self, email: str, password: str) -> dict[str, Any]:
        """Login with email/password."""
        url = f"{self.config.server}/auth/login"
        payload = {"email": email, "password": password}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        # Update config with tokens
        self.config.access_token = data["access_token"]
        self.config.refresh_token = data["refresh_token"]
        self.config.email = email
        self._setup_auth()

        return data
