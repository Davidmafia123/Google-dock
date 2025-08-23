from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.async_api import Page

from ..core.models import SearchResult


class AbstractSearchEngine(ABC):
    """Abstract base class for a search engine."""

    @abstractmethod
    async def search(
        self, query: str, page: Optional[Page] = None
    ) -> List[SearchResult]:
        """
        Performs a search for the given query.

        Args:
            query: The search query string.
            page: An optional Playwright Page object for browser-based engines.

        Returns:
            A list of SearchResult objects.
        """
        pass
