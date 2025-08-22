import asyncio
from playwright.async_api import Page
import rich

# A list of common selectors for CAPTCHA iframes or elements.
CAPTCHA_SELECTORS = [
    'iframe[src*="recaptcha"]',
    'iframe[src*="hcaptcha"]',
    'div#g-recaptcha',
    'div#h-captcha',
]

async def check_for_captcha(page: Page) -> bool:
    """
    Checks if a CAPTCHA is present on the page by looking for common selectors.

    Args:
        page: The Playwright Page object to check.

    Returns:
        True if a CAPTCHA is detected, False otherwise.
    """
    for selector in CAPTCHA_SELECTORS:
        try:
            # Use a short timeout to quickly check for the presence of the element.
            await page.wait_for_selector(selector, state='visible', timeout=2000)
            rich.print(f"[yellow]Potential CAPTCHA detected with selector: {selector}[/yellow]")
            return True
        except:
            # The selector was not found, continue to the next one.
            continue
    return False

async def solve_captcha_manually(page: Page):
    """
    If a CAPTcha is detected, this function will pause execution
    and prompt the user to solve it manually in the browser.
    """
    if await check_for_captcha(page):
        rich.print("\n[bold yellow]CAPTCHA Detected![/bold yellow]")
        rich.print("The browser may be waiting for you to prove you're not a robot.")
        rich.print("Please solve the CAPTCHA in the browser window.")
        rich.print("Once you have passed the check, press [bold]Enter[/bold] here to continue...")

        loop = asyncio.get_running_loop()
        # Run the blocking input() call in a separate thread to avoid blocking the event loop.
        await loop.run_in_executor(None, input)

        rich.print("[green]Resuming execution...[/green]")
    else:
        rich.print("[green]No CAPTCHA detected.[/green]")
