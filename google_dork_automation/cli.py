import asyncio
from pathlib import Path
import typer
from typing_extensions import Annotated
import rich

from rich.table import Table

from google_dork_automation.core.config import load_config, Config
from google_dork_automation.browser.playwright_factory import PlaywrightManager
from google_dork_automation.search.cse import CseSearchEngine
from google_dork_automation.search.google import GoogleSearchEngine
from google_dork_automation.core.templates import load_templates
from google_dork_automation.storage.exporters import CsvExporter, JsonLinesExporter
from google_dork_automation.storage.sqlite import SqliteStorage
from google_dork_automation.core.models import SearchResult
from typing import List

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


async def run_browser_search(query: str, config: Config, attach: bool) -> List[SearchResult]:
    """Runs the search using the browser-based Google engine."""
    rich.print("[blue]Using browser-based Google Search...[/blue]")
    manager = PlaywrightManager(config)
    all_results = []
    try:
        context = await manager.start_get_context(attach=attach)
        page = await context.new_page()
        rich.print("[green]Browser context created.[/green]")

        engine = GoogleSearchEngine(config)
        results = await engine.search(query=query, page=page)

        if not results:
            rich.print("[yellow]No results found.[/yellow]")
        else:
            rich.print(f"[green]Found {len(results)} results.[/green]")

        all_results.extend(results)
        await page.close()
    finally:
        await manager.close()
        rich.print("[green]Browser resources released.[/green]")
    return all_results

async def run_cse_search(query: str, config: Config) -> List[SearchResult]:
    """Runs the search using the Google CSE API."""
    rich.print("[blue]Using Google Custom Search Engine (CSE)...[/blue]")
    engine = CseSearchEngine(config)
    try:
        # Pass page=None as it's not used by this engine
        results = await engine.search(query=query, page=None)
        if not results:
            rich.print("[yellow]No results found.[/yellow]")
        else:
            rich.print(f"[green]Found {len(results)} results.[/green]")
        return results
    finally:
        await engine.close()


async def main_async_logic(
    dorks_to_run: List[str],
    config: Config,
    google: bool,
    cse: bool,
    attach: bool,
    output_csv: Path,
    output_jsonl: Path,
    output_sqlite: Path,
):
    """The core async logic for running searches and saving results."""
    all_results = []

    for dork_query in dorks_to_run:
        rich.print(f"Executing query: [bold]'{dork_query}'[/bold]")
        results = []
        if google:
            results = await run_browser_search(dork_query, config, attach)
        elif cse:
            results = await run_cse_search(dork_query, config)

        all_results.extend(results)
        # Optional: Add a delay here from stealth config

    if not all_results:
        rich.print("[bold yellow]Finished running all dorks. No results to save.[/bold yellow]")
        return

    # --- Save Results ---
    rich.print(f"\n[bold]Total results to save: {len(all_results)}[/bold]")
    if output_csv:
        CsvExporter().write(all_results, output_csv)
    if output_jsonl:
        JsonLinesExporter().write(all_results, output_jsonl)
    if output_sqlite:
        storage = SqliteStorage(output_sqlite)
        await storage.init_db()
        await storage.save_results(all_results)
        await storage.close()


@app.command(name="search", help="Execute a search using a specified backend.")
def search_command(
    # Input options
    query: Annotated[
        str, typer.Option(help="A single Google Dork query to execute.")
    ] = None,
    template: Annotated[
        str, typer.Option(help="The name of the dork template to use.")
    ] = None,

    # Config options
    config_file: Annotated[
        Path, typer.Option("--config", help="Path to the configuration file.")
    ] = Path("config.yaml"),

    # Backend options
    google: Annotated[
        bool,
        typer.Option("--google", help="Use the browser-based Google search."),
    ] = False,
    cse: Annotated[
        bool,
        typer.Option("--cse", help="Use the Google Custom Search Engine API."),
    ] = False,

    # Browser options
    attach: Annotated[
        bool,
        typer.Option(
            "--attach",
            help="Attach to a running Chrome instance (only with --google).",
        ),
    ] = False,

    # Output options
    output_csv: Annotated[
        Path, typer.Option(help="Path to save results in CSV format.")
    ] = None,
    output_jsonl: Annotated[
        Path, typer.Option(help="Path to save results in JSON-Lines format.")
    ] = None,
    output_sqlite: Annotated[
        Path, typer.Option(help="Path to save results in a SQLite database.")
    ] = None,
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

        asyncio.run(main_async_logic(
            dorks_to_run=dorks_to_run,
            config=config,
            google=google,
            cse=cse,
            attach=attach,
            output_csv=output_csv,
            output_jsonl=output_jsonl,
            output_sqlite=output_sqlite,
        ))

    except FileNotFoundError:
        rich.print(f"[bold red]Error: Configuration file not found at '{config_file}'[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
