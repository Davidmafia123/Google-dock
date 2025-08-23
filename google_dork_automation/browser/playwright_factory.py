from __future__ import annotations
from typing import Optional

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Playwright,
    PlaywrightContextManager,
)
from google_dork_automation.core.config import Config

class PlaywrightManager:
    """
    Manages the Playwright browser instance, either by launching a new one
    or connecting to an existing one.
    """

    def __init__(self, config: Config):
        self.config = config
        self._pw_manager: Optional[PlaywrightContextManager] = None
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._did_launch_browser: bool = False

    async def start_get_context(
        self, attach: bool = False, remote_debugging_port: int = 9222
    ) -> BrowserContext:
        """
        Starts the Playwright manager, launches or connects to a browser,
        and returns a browser context.
        """
        self._pw_manager = async_playwright()
        self._playwright = await self._pw_manager.__aenter__()

        if attach:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{remote_debugging_port}"
            )
            self._did_launch_browser = False
            # Return the default context from the attached browser
            return self._browser.contexts[0]
        else:
            self._browser = await self._playwright.chromium.launch(
                headless=self.config.browser.headless
            )
            self._did_launch_browser = True
            # Return a new context from the launched browser
            return await self._browser.new_context(
                viewport=self.config.browser.viewport.model_dump(),
                user_agent=(
                    self.config.stealth.user_agents[0]
                    if self.config.stealth.user_agents
                    else None
                ),
            )

    async def close(self):
        """
        Closes the browser if it was launched, and stops the Playwright manager.
        """
        # Note: Contexts created from a launched browser are closed when the browser is closed.
        # Contexts from an attached browser are not our responsibility to close.
        if self._browser and self._did_launch_browser:
            await self._browser.close()

        if self._pw_manager:
            await self._pw_manager.__aexit__(None, None, None)
