"""HTTP client for KB.se API."""

from typing import Any, cast

import httpx


class KBClient:
    """HTTP client for KB.se API."""

    BASE_URL = "https://data.kb.se/search/"

    def __init__(self, timeout: int = 30):
        """Initialize KB client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout, headers={"Accept": "application/json"})

    def search(
        self,
        query: str,
        journal: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict[str, Any]:
        """Execute search query.

        Args:
            query: Search phrase (or "*" for wildcard)
            journal: Journal name (None or "None" for all journals)
            from_date: Start date (YYYY-MM-DD format)
            to_date: End date (YYYY-MM-DD format)

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPError: If request fails
        """
        # Build parameters
        params: dict[str, str] = {
            "q": query if query != "*" else "*",
            "searchGranularity": "part",
            "limit": "1",
        }

        # Add optional parameters
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if journal and journal.lower() != "none":
            params["isPartOf"] = journal

        # Execute request with explicit JSON accept header
        response = self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()

        # Verify we got JSON
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            raise ValueError(f"Expected JSON response, got {content_type}")

        return cast(dict[str, Any], response.json())

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def __enter__(self) -> "KBClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
