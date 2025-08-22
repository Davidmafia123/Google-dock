from pathlib import Path
import typer
from typing_extensions import Annotated
import rich

from google_dork_automation.core.config import load_config

app = typer.Typer()


@app.command()
def main(
    query: Annotated[
        str, typer.Option(help="The Google Dork query to execute.")
    ] = "intitle:\"index of\"",
    config_file: Annotated[
        Path, typer.Option("--config", help="Path to the configuration file.")
    ] = Path("config.yaml"),
):
    """
    Google Dorking Automation Tool
    """
    try:
        config = load_config(config_file)
        rich.print(f"Configuration loaded from '{config_file}'.")
        rich.print(f"Executing query: '{query}'")
        # Placeholder for actual dorking logic
    except FileNotFoundError:
        rich.print(f"[bold red]Error: Configuration file not found at '{config_file}'[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
