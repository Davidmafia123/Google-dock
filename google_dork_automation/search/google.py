from typing import List
from datetime import datetime, timezone
from playwright.async_api import Page
import rich

from .base import AbstractSearchEngine
from ..core.models import SearchResult
from ..core.config import Config
from ..browser.captcha import solve_captcha_manually

class GoogleSearchEngine(AbstractSearchEngine):
    """A search engine that scrapes results directly from the Google search page."""

    BASE_URL = "https://www.google.com"

    def __init__(self, config: Config):
        self.config = config

    async def search(self, query: str, page: Page = None) -> List[SearchResult]:
        """
        Performs a search by navigating on a Playwright page and scraping results.

        Args:
            query: The search query string.
            page: The Playwright Page object to use for the search.

        Returns:
            A list of SearchResult objects.
        """
        if page is None:
            raise ValueError("GoogleSearchEngine requires a Playwright Page object.")

        search_url = f"{self.BASE_URL}/search?q={query}"
        rich.print(f"Navigating to {search_url}...")

        try:
            await page.goto(search_url, wait_until="domcontentloaded")
            await solve_captcha_manually(page)

            # This selector targets the main container for search results.
            await page.wait_for_selector("div#search", timeout=10000)

            # These selectors are based on Google's current HTML structure.
            result_container_selector = "div.g"
            title_selector = "h3"
            link_selector = "a"
            snippet_selector = "div[data-sncf='2']"

            results = []
            result_elements = await page.query_selector_all(result_container_selector)

            rich.print(f"Found {len(result_elements)} potential result elements on the page.")

            for element in result_elements:
                try:
                    title_element = await element.query_selector(title_selector)
                    link_element = await element.query_selector(link_selector)
                    snippet_element = await element.query_selector(snippet_selector)

                    if title_element and link_element and snippet_element:
                        title = await title_element.inner_text()
                        url = await link_element.get_attribute("href")
                        snippet = await snippet_element.inner_text()

                        if url and url.startswith("http"):
                            results.append(
                                SearchResult(
                                    title=title,
                                    url=url,
                                    snippet=snippet,
                                    timestamp=datetime.now(timezone.utc)
                                )
                            )
                except Exception as e:
                    rich.print(f"[yellow]Could not parse a result element: {e}[/yellow]")

            return results

        except Exception as e:
            rich.print(f"[bold red]An error occurred during browser search: {e}[/bold red]")
            try:
                await page.screenshot(path="error_screenshot.png")
                rich.print("[yellow]Screenshot saved to error_screenshot.png[/yellow]")
            except Exception as screenshot_error:
                rich.print(f"[red]Could not save screenshot: {screenshot_error}[/red]")
            return []
