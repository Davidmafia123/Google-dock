import pytest
import respx
from httpx import Response

from google_dork_automation.core.config import Config
from google_dork_automation.search.cse import CseSearchEngine
from google_dork_automation.core.models import SearchResult

@pytest.fixture
def mock_config():
    """Fixture to create a valid Config object for CSE tests."""
    config_dict = {
        "browser": {}, # Not used in this test
        "search": {
            "google": {}, # Not used
            "cse": {"api_key": "test_api_key", "cx": "test_cx_id", "safe": "off"},
        },
        "stealth": {}, # Not used
        "storage": {}, # Not used
    }
    # Manually fill in nested models to avoid validation errors for unused parts
    config_dict["browser"] = {"headless": True, "viewport": {"width": 1, "height": 1}}
    config_dict["stealth"] = {"user_agents": [], "min_delay": 0, "max_delay": 0}
    config_dict["storage"] = {"db_path": "", "html_template": ""}
    config_dict["search"]["google"] = {"tbs": ""}
    return Config.model_validate(config_dict)

@pytest.mark.asyncio
@respx.mock
async def test_cse_search_success(mock_config):
    """Tests a successful search call that returns results."""
    # Mock the API endpoint
    mock_api_response = {
        "items": [
            {
                "title": "Test Result 1",
                "link": "https://example.com/1",
                "snippet": "This is the first test result.",
            },
            {
                "title": "Test Result 2",
                "link": "https://example.com/2",
                "snippet": "This is the second test result.",
            },
        ]
    }
    respx.get(CseSearchEngine.BASE_URL).mock(return_value=Response(200, json=mock_api_response))

    engine = CseSearchEngine(mock_config)
    results = await engine.search("test query")
    await engine.close()

    assert len(results) == 2
    assert all(isinstance(r, SearchResult) for r in results)
    assert results[0].title == "Test Result 1"
    assert str(results[1].url) == "https://example.com/2"

@pytest.mark.asyncio
@respx.mock
async def test_cse_search_no_results(mock_config):
    """Tests a successful search call that returns no results."""
    mock_api_response = {"items": []} # No items in the response
    respx.get(CseSearchEngine.BASE_URL).mock(return_value=Response(200, json=mock_api_response))

    engine = CseSearchEngine(mock_config)
    results = await engine.search("a query with no results")
    await engine.close()

    assert len(results) == 0

@pytest.mark.asyncio
@respx.mock
async def test_cse_search_api_error(mock_config, capsys):
    """Tests the handling of an API error (e.g., 400 Bad Request)."""
    error_response = {"error": {"message": "API key not valid"}}
    respx.get(CseSearchEngine.BASE_URL).mock(return_value=Response(400, json=error_response))

    engine = CseSearchEngine(mock_config)
    results = await engine.search("test query")
    await engine.close()

    assert len(results) == 0

    # Check that an error message was printed to the console
    captured = capsys.readouterr()
    assert "HTTP error occurred" in captured.out
    assert "API key not valid" in captured.out
