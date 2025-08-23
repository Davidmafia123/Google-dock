import asyncio
from pathlib import Path
import typer
from typing_extensions import Annotated
import rich

from google_dork_automation.core.config import load_config, Config
from google_dork_automation.browser.playwright_factory import PlaywrightManager
from google_dork_automation.search.cse import CseSearchEngine

app = typer.Typer()


async def run_browser_search(query: str, config: Config, attach: bool):
    """Runs the search using the browser-based Google engine."""
    rich.print("[blue]Using browser-based Google Search...[/blue]")
    manager = PlaywrightManager(config)
    try:
        context = await manager.get_browser_context(attach=attach)
        page = await context.new_page()
        rich.print("[green]Browser launched successfully.[/green]")

        await page.goto("https://www.google.com")
        rich.print(f"Page title: [bold]{await page.title()}[/bold]")
        # Placeholder for actual search logic
        await asyncio.sleep(2)

        await page.close()
    finally:
        await manager.close()
        rich.print("[green]Browser closed.[/green]")

async def run_cse_search(query: str, config: Config):
    """Runs the search using the Google CSE API."""
    rich.print("[blue]Using Google Custom Search Engine (CSE)...[/blue]")
    engine = CseSearchEngine(config)
    try:
        results = await engine.search(query)
        if not results:
            rich.print("[yellow]No results found.[/yellow]")
            return

        rich.print(f"[green]Found {len(results)} results:[/green]")
        for result in results:
            rich.print(f"  - [bold cyan]{result.title}[/bold cyan]")
            rich.print(f"    [dim]{result.url}[/dim]")
    finally:
        await engine.close()


@app.command()
def main(
    query: Annotated[
        str, typer.Option(help="The Google Dork query to execute.")
    ] = "intitle:\"index of\"",
    config_file: Annotated[
        Path, typer.Option("--config", help="Path to the configuration file.")
    ] = Path("config.yaml"),
    google: Annotated[
        bool,
        typer.Option("--google", help="Use the browser-based Google search."),
    ] = False,
    cse: Annotated[
        bool,
        typer.Option("--cse", help="Use the Google Custom Search Engine API."),
    ] = False,
    attach: Annotated[
        bool,
        typer.Option(
            "--attach",
            help="Attach to a running Chrome instance (only with --google).",
        ),
    ] = False,
):
    """
    Google Dorking Automation Tool
    """
    if not google and not cse:
        rich.print("[bold red]Error: Please specify a search backend (--google or --cse).[/bold red]")
        raise typer.Exit(code=1)
    if google and cse:
        rich.print("[bold red]Error: Please choose only one search backend (--google or --cse).[/bold red]")
        raise typer.Exit(code=1)
    if attach and not google:
        rich.print("[bold red]Error: --attach can only be used with --google.[/bold red]")
        raise typer.Exit(code=1)

    try:
        config = load_config(config_file)
        rich.print(f"Configuration loaded from '{config_file}'.")
        rich.print(f"Executing query: '{query}'")

        if google:
            asyncio.run(run_browser_search(query, config, attach))
        elif cse:
            asyncio.run(run_cse_search(query, config))

    except FileNotFoundError:
        rich.print(f"[bold red]Error: Configuration file not found at '{config_file}'[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
