import httpx
from typing import List
from datetime import datetime, timezone
import rich

from .base import AbstractSearchEngine
from ..core.models import SearchResult
from ..core.config import Config

class CseSearchEngine(AbstractSearchEngine):
    """A search engine that uses the Google Custom Search Engine (CSE) JSON API."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, config: Config):
        self.config = config.search.cse
        self.client = httpx.AsyncClient()

    async def search(self, query: str) -> List[SearchResult]:
        """
        Performs a search using the Google CSE API.

        Args:
            query: The search query string.

        Returns:
            A list of SearchResult objects, or an empty list if the search fails.
        """
        params = {
            "key": self.config.api_key,
            "cx": self.config.cx,
            "q": query,
            "safe": self.config.safe,
        }

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            data = response.json()
            items = data.get("items", [])

            results = []
            for item in items:
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        timestamp=datetime.now(timezone.utc),
                    )
                )
            return results

        except httpx.HTTPStatusError as e:
            rich.print(f"[bold red]HTTP error occurred: {e}[/bold red]")
            rich.print(f"[bold red]Response content: {e.response.text}[/bold red]")
            return []
        except Exception as e:
            rich.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
            return []

    async def close(self):
        """Closes the httpx client."""
        await self.client.aclose()
