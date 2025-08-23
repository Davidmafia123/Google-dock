from abc import ABC, abstractmethod
from typing import List
from ..core.models import SearchResult

class AbstractSearchEngine(ABC):
    """Abstract base class for a search engine."""

    @abstractmethod
    async def search(self, query: str) -> List[SearchResult]:
        """
        Performs a search for the given query.

        Args:
            query: The search query string.

        Returns:
            A list of SearchResult objects.
        """
        pass
