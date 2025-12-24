"""Cloud API client for hwdocs-mcp - quota management only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .config import Config


@dataclass
class QuotaStatus:
    """User's quota status."""

    plan: str
    monthly_limit: int
    used_pages: int
    remaining_pages: int
    resets_at: str


class CloudApiError(Exception):
    """Error from cloud API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class QuotaExceededError(CloudApiError):
    """User's quota has been exceeded."""

    pass


class AuthenticationError(CloudApiError):
    """Authentication failed."""

    pass


class CloudApiClient:
    """Client for the hwdocs cloud API - quota management only."""

    def __init__(self, config: Config | None = None):
        """Initialize the client."""
        self.config = config or Config.load()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> CloudApiClient:
        """Enter async context."""
        self._client = httpx.AsyncClient(
            base_url=self.config.api_base,
            timeout=httpx.Timeout(60.0, connect=10.0),
            trust_env=False,  # Ignore system proxy to avoid connection issues
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        if self._client:
            await self._client.aclose()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        if not self.config.api_token:
            raise AuthenticationError(
                "No API token configured. Run 'hwdocs login' to authenticate.",
                status_code=401,
            )
        return {"Authorization": f"Bearer {self.config.api_token}"}

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an authenticated request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        response = await self._client.request(method, path, headers=headers, **kwargs)

        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed. Your token may be invalid or expired.",
                status_code=401,
            )
        if response.status_code == 402:
            data = response.json()
            raise QuotaExceededError(
                data.get("detail", "Quota exceeded. Upgrade your plan for more pages."),
                status_code=402,
            )
        if response.status_code >= 400:
            try:
                data = response.json()
                message = data.get("detail", response.text)
            except Exception:
                message = response.text
            raise CloudApiError(message, status_code=response.status_code)

        return response

    async def get_quota(self) -> QuotaStatus:
        """Get current quota status."""
        response = await self._request("GET", "/quota")
        data = response.json()
        return QuotaStatus(
            plan=data["plan"],
            monthly_limit=data["monthly_limit"],
            used_pages=data["used_pages"],
            remaining_pages=data["remaining_pages"],
            resets_at=data["resets_at"],
        )

    async def deduct_quota(self, pages: int) -> QuotaStatus:
        """
        Deduct pages from quota after successful parse.

        Args:
            pages: Number of pages to deduct.

        Returns:
            Updated quota status.

        Raises:
            QuotaExceededError: If not enough quota remaining.
            AuthenticationError: If authentication fails.
            CloudApiError: For other API errors.
        """
        response = await self._request(
            "POST",
            "/quota/deduct",
            json={"pages": pages},
        )
        data = response.json()
        return QuotaStatus(
            plan=data.get("plan", "unknown"),
            monthly_limit=data.get("monthly_limit", 0),
            used_pages=data.get("used_pages", 0),
            remaining_pages=data.get("remaining_pages", 0),
            resets_at=data.get("resets_at", ""),
        )
