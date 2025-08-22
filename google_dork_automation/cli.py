import asyncio
from pathlib import Path
import typer
from typing_extensions import Annotated
import rich

from google_dork_automation.core.config import load_config, Config
from google_dork_automation.browser.playwright_factory import PlaywrightManager

app = typer.Typer()


async def async_main(
    query: str,
    config: Config,
    attach: bool,
):
    """The core async logic of the application."""
    manager = PlaywrightManager(config)
    try:
        context = await manager.get_browser_context(attach=attach)
        page = await context.new_page()
        rich.print("[green]Browser launched successfully.[/green]")

        await page.goto("https://www.google.com")
        rich.print(f"Page title: [bold]{await page.title()}[/bold]")

        # Here is where we would eventually run the search logic
        await asyncio.sleep(5) # Keep browser open for 5s for verification

        await page.close()
    finally:
        await manager.close()
        rich.print("[green]Browser closed.[/green]")


@app.command()
def main(
    query: Annotated[
        str, typer.Option(help="The Google Dork query to execute.")
    ] = "intitle:\"index of\"",
    config_file: Annotated[
        Path, typer.Option("--config", help="Path to the configuration file.")
    ] = Path("config.yaml"),
    attach: Annotated[
        bool,
        typer.Option(
            "--attach",
            help="Attach to a running Chrome instance with remote debugging.",
        ),
    ] = False,
):
    """
    Google Dorking Automation Tool
    """
    try:
        config = load_config(config_file)
        rich.print(f"Configuration loaded from '{config_file}'.")
        rich.print(f"Executing query: '{query}'")

        asyncio.run(async_main(query, config, attach))

    except FileNotFoundError:
        rich.print(f"[bold red]Error: Configuration file not found at '{config_file}'[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
