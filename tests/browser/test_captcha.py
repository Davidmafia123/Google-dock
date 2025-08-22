import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from google_dork_automation.browser.captcha import check_for_captcha, solve_captcha_manually

@pytest.mark.asyncio
async def test_check_for_captcha_found():
    """Tests that check_for_captcha returns True when a captcha selector is found."""
    mock_page = AsyncMock()
    # Simulate wait_for_selector succeeding on the first try
    mock_page.wait_for_selector.return_value = True

    result = await check_for_captcha(mock_page)

    assert result is True
    mock_page.wait_for_selector.assert_called_once()

@pytest.mark.asyncio
async def test_check_for_captcha_not_found():
    """Tests that check_for_captcha returns False when no captcha selectors are found."""
    mock_page = AsyncMock()
    # Simulate wait_for_selector timing out
    mock_page.wait_for_selector.side_effect = asyncio.TimeoutError

    result = await check_for_captcha(mock_page)

    assert result is False
    # It should be called for each selector in the list
    from google_dork_automation.browser.captcha import CAPTCHA_SELECTORS
    assert mock_page.wait_for_selector.call_count == len(CAPTCHA_SELECTORS)

@pytest.mark.asyncio
@patch("google_dork_automation.browser.captcha.check_for_captcha", new_callable=AsyncMock)
@patch("google_dork_automation.browser.captcha.asyncio.get_running_loop")
async def test_solve_captcha_manually_when_captcha_is_present(mock_get_loop, mock_check_captcha):
    """
    Tests that the user is prompted for input when a CAPTCHA is detected.
    """
    mock_page = MagicMock()
    mock_check_captcha.return_value = True # Simulate captcha found

    # Mock the loop and executor to check the input call
    mock_loop = AsyncMock()
    mock_get_loop.return_value = mock_loop

    await solve_captcha_manually(mock_page)

    mock_check_captcha.assert_called_once_with(mock_page)
    # Check that input() was called via the executor
    mock_loop.run_in_executor.assert_called_once()

@pytest.mark.asyncio
@patch("google_dork_automation.browser.captcha.check_for_captcha", new_callable=AsyncMock)
@patch("rich.print")
async def test_solve_captcha_manually_when_no_captcha(mock_print, mock_check_captcha):
    """
    Tests that nothing happens when no CAPTCHA is detected.
    """
    mock_page = MagicMock()
    mock_check_captcha.return_value = False # Simulate no captcha

    await solve_captcha_manually(mock_page)

    mock_check_captcha.assert_called_once_with(mock_page)
    # Check that the "No CAPTCHA detected" message is printed
    mock_print.assert_called_with("[green]No CAPTCHA detected.[/green]")
