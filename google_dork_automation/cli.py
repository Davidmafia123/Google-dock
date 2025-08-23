import asyncio
from pathlib import Path
import typer
from typing_extensions import Annotated
import rich

from rich.table import Table

from google_dork_automation.core.config import load_config, Config
from google_dork_automation.browser.playwright_factory import PlaywrightManager
from google_dork_automation.search.cse import CseSearchEngine
from google_dork_automation.core.templates import load_templates

app = typer.Typer(help="Google Dorking Automation Tool")
templates_app = typer.Typer(help="Manage dork templates.")
app.add_typer(templates_app, name="templates")

@templates_app.command("list")
def list_templates():
    """Lists all available dork templates."""
    templates = load_templates()
    if not templates:
        rich.print("[yellow]No dork templates found.[/yellow]")
        return

    table = Table(title="Available Dork Templates")
    table.add_column("Template Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Dork Count", justify="right", style="green")

    for name, data in templates.items():
        description = data.get("description", "No description")
        dork_count = len(data.get("dorks", []))
        table.add_row(name, description, str(dork_count))

    rich.print(table)


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


@app.command(name="search", help="Execute a search using a specified backend.")
def search_command(
    query: Annotated[
        str, typer.Option(help="A single Google Dork query to execute.")
    ] = None,
    template: Annotated[
        str, typer.Option(help="The name of the dork template to use.")
    ] = None,
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
    # --- Argument Validation ---
    if query is None and template is None:
        rich.print("[bold red]Error: Please provide a dork using --query or --template.[/bold red]")
        raise typer.Exit(code=1)
    if query is not None and template is not None:
        rich.print("[bold red]Error: --query and --template are mutually exclusive.[/bold red]")
        raise typer.Exit(code=1)
    if not google and not cse:
        rich.print("[bold red]Error: Please specify a search backend (--google or --cse).[/bold red]")
        raise typer.Exit(code=1)
    if google and cse:
        rich.print("[bold red]Error: Please choose only one search backend (--google or --cse).[/bold red]")
        raise typer.Exit(code=1)
    if attach and not google:
        rich.print("[bold red]Error: --attach can only be used with --google.[/bold red]")
        raise typer.Exit(code=1)

    # --- Dork Collection ---
    dorks_to_run = []
    if query:
        dorks_to_run.append(query)
    elif template:
        templates = load_templates()
        if template not in templates:
            rich.print(f"[bold red]Error: Template '{template}' not found.[/bold red]")
            rich.print("Use 'gda templates list' to see available templates.")
            raise typer.Exit(code=1)
        dorks_to_run.extend(templates[template].get("dorks", []))

    if not dorks_to_run:
        rich.print("[yellow]No dorks to run.[/yellow]")
        raise typer.Exit()

    # --- Execution ---
    try:
        config = load_config(config_file)
        rich.print(f"Configuration loaded from '{config_file}'.")

        for dork_query in dorks_to_run:
            rich.print(f"Executing query: [bold]'{dork_query}'[/bold]")
            if google:
                asyncio.run(run_browser_search(dork_query, config, attach))
            elif cse:
                asyncio.run(run_cse_search(dork_query, config))
            # Optional: Add a delay here from stealth config

    except FileNotFoundError:
        rich.print(f"[bold red]Error: Configuration file not found at '{config_file}'[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
