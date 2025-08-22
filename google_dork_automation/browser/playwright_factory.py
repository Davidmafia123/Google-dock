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
        self._context: Optional[BrowserContext] = None
        self._did_launch_browser: bool = False

    async def get_browser_context(
        self, attach: bool = False, remote_debugging_port: int = 9222
    ) -> BrowserContext:
        """
        Starts Playwright and returns a browser context.

        Args:
            attach: If True, attaches to a running browser. Otherwise, launches a new one.
            remote_debugging_port: The port for the remote debugging protocol.

        Returns:
            A Playwright BrowserContext.
        """
        self._pw_manager = async_playwright()
        self._playwright = await self._pw_manager.start()

        if attach:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{remote_debugging_port}"
            )
            self._context = self._browser.contexts[0]
            self._did_launch_browser = False
        else:
            user_data_dir = self.config.browser.user_data_dir
            browser_args = {"headless": self.config.browser.headless}
            context_args = {
                "viewport": self.config.browser.viewport.model_dump(),
                "user_agent": (
                    self.config.stealth.user_agents[0]
                    if self.config.stealth.user_agents
                    else None
                ),
            }

            if user_data_dir:
                self._context = await self._playwright.chromium.launch_persistent_context(
                    user_data_dir, **browser_args, **context_args
                )
                self._browser = self._context.browser
            else:
                self._browser = await self._playwright.chromium.launch(**browser_args)
                self._context = await self._browser.new_context(**context_args)

            self._did_launch_browser = True

        return self._context

    async def close(self):
        """
        Closes the browser context and stops Playwright.
        If attached to a browser, it will only disconnect, not close the browser itself.
        If the browser was launched, it will be closed.
        """
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass

        if self._browser and self._browser.is_connected() and self._did_launch_browser:
            await self._browser.close()

        if self._pw_manager:
            await self._pw_manager.stop()
