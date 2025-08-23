import pytest
from unittest.mock import AsyncMock, MagicMock

from google_dork_automation.core.config import Config
from google_dork_automation.browser.playwright_factory import PlaywrightManager

@pytest.fixture
def mock_config():
    """Fixture to create a mock Config object for testing."""
    config_dict = {
        "browser": {
            "headless": True,
            "user_data_dir": None,
            "viewport": {"width": 1280, "height": 720},
        },
        "search": {
            "google": {"tbs": "qdr:d"},
            "cse": {"api_key": "dummy_key", "cx": "dummy_cx", "safe": "off"},
        },
        "stealth": {
            "user_agents": ["TestAgent/1.0"],
            "min_delay": 1,
            "max_delay": 5,
            "proxy_file": None,
        },
        "storage": {
            "db_path": "dummy.db",
            "html_template": "template.html",
        },
    }
    return Config.model_validate(config_dict)

@pytest.mark.asyncio
async def test_playwright_manager_launch_mode(mocker, mock_config):
    """Tests that the manager calls launch() in auto mode."""
    mock_pw_manager = AsyncMock()
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()

    mocker.patch(
        "google_dork_automation.browser.playwright_factory.async_playwright",
        return_value=mock_pw_manager,
    )
    # Mock the context manager's __aenter__ to return the playwright instance
    mock_pw_manager.__aenter__.return_value = mock_playwright_instance
    mock_playwright_instance.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context

    manager = PlaywrightManager(mock_config)
    context = await manager.start_get_context(attach=False)

    mock_pw_manager.__aenter__.assert_awaited_once()
    mock_playwright_instance.chromium.launch.assert_called_once()
    mock_browser.new_context.assert_called_once()
    assert context == mock_context
    assert manager._did_launch_browser is True

    await manager.close()
    mock_browser.close.assert_called_once()
    mock_pw_manager.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_playwright_manager_attach_mode(mocker, mock_config):
    """Tests that the manager calls connect_over_cdp() in attach mode."""
    mock_pw_manager = AsyncMock()
    mock_playwright_instance = AsyncMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_browser.contexts = [mock_context]

    mocker.patch(
        "google_dork_automation.browser.playwright_factory.async_playwright",
        return_value=mock_pw_manager,
    )
    mock_pw_manager.__aenter__.return_value = mock_playwright_instance
    mock_playwright_instance.chromium.connect_over_cdp.return_value = mock_browser

    manager = PlaywrightManager(mock_config)
    context = await manager.start_get_context(attach=True)

    mock_pw_manager.__aenter__.assert_awaited_once()
    mock_playwright_instance.chromium.connect_over_cdp.assert_called_once_with("http://127.0.0.1:9222")
    assert context == mock_context
    assert manager._did_launch_browser is False

    mock_browser.close = AsyncMock()
    await manager.close()
    mock_browser.close.assert_not_called()
    mock_pw_manager.__aexit__.assert_awaited_once()
