import pytest
from datetime import datetime
from pydantic import ValidationError

from google_dork_automation.core.dork import Dork
from google_dork_automation.core.models import SearchResult

def test_dork_creation():
    """Tests that a Dork object can be created successfully."""
    dork = Dork(query="inurl:admin intitle:\"Login\"")
    assert dork.query == "inurl:admin intitle:\"Login\""

def test_search_result_creation():
    """Tests that a SearchResult object can be created successfully with valid data."""
    now = datetime.now()
    result = SearchResult(
        title="Example Domain",
        url="https://example.com",
        snippet="This is an example snippet for a search result.",
        timestamp=now
    )
    assert result.title == "Example Domain"
    assert str(result.url) == "https://example.com/"  # Pydantic HttpUrl adds a trailing slash
    assert result.snippet == "This is an example snippet for a search result."
    assert result.timestamp == now

def test_search_result_invalid_url():
    """Tests that creating a SearchResult with an invalid URL raises a ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        SearchResult(
            title="Invalid URL Test",
            url="not-a-valid-url",
            snippet="This should fail.",
            timestamp=datetime.now()
        )
    # Check that the error message is about the URL field
    assert "url" in str(excinfo.value)

def test_dork_empty_query():
    """Tests that a Dork object can be created with an empty query string."""
    dork = Dork(query="")
    assert dork.query == ""

def test_search_result_url_types():
    """Tests that various valid URL types are handled correctly."""
    now = datetime.now()

    # Test with http
    result_http = SearchResult(
        title="HTTP Test",
        url="http://example.com/path?query=param",
        snippet="Snippet",
        timestamp=now
    )
    assert str(result_http.url) == "http://example.com/path?query=param"

    # Pydantic's HttpUrl is strict and only allows http/https by default,
    # which is sufficient for this tool's purposes.
