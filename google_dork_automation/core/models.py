from pydantic import BaseModel, HttpUrl
from datetime import datetime

class SearchResult(BaseModel):
    """Represents a single search result."""
    title: str
    url: HttpUrl
    snippet: str
    timestamp: datetime
