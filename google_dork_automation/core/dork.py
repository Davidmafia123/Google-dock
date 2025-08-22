from pydantic import BaseModel

class Dork(BaseModel):
    """Represents a single Google Dork query."""
    query: str
