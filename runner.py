#!/usr/bin/env python
"""
An interactive runner script to guide users through running a search.
"""

import sys
import subprocess
from pathlib import Path

# Add the project root to the path to allow imports from the package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

from google_dork_automation.core.templates import load_templates

console = Console()

def welcome():
    """Prints a welcome message."""
    console.print(Panel(
        "[bold green]Welcome to the Google Dorking Automation Tool![/bold green]\n\n"
        "This script will guide you through setting up and running a search.",
        title="[bold cyan]GDA Runner[/bold cyan]",
        border_style="cyan"
    ))

def get_search_type():
    """Asks the user if they want to use a single query or a template."""
    return Prompt.ask(
        "How do you want to specify your dorks?",
        choices=["single", "template"],
        default="template"
    )

def get_dork_from_user():
    """Prompts the user for a single dork query."""
    return Prompt.ask("[bold]Enter your Google Dork query[/bold]")

def get_template_from_user():
    """Shows available templates and asks the user to choose one."""
    templates = load_templates()
    if not templates:
        console.print("[bold red]No templates found. Exiting.[/bold red]")
        sys.exit(1)

    table = Table(title="Available Dork Templates")
    table.add_column("No.", style="yellow")
    table.add_column("Template Name", style="cyan")
    table.add_column("Description")

    template_names = list(templates.keys())
    for i, name in enumerate(template_names):
        table.add_row(str(i + 1), name, templates[name].get("description", ""))

    console.print(table)
    choice = IntPrompt.ask(
        "Choose a template number",
        choices=[str(i + 1) for i in range(len(template_names))],
        show_choices=False
    )
    return template_names[choice - 1]

def get_backend():
    """Asks the user to choose a search backend."""
    return Prompt.ask(
        "Which search backend do you want to use?",
        choices=["cse", "google"],
        default="cse"
    )

def get_output_file():
    """Asks for an output filename."""
    return Prompt.ask(
        "[bold]Enter a filename to save the results[/bold] (e.g., results.xlsx, results.csv, results.jsonl, results.db)",
        default="results.xlsx"
    )

def main():
    """Main interactive workflow."""
    welcome()

    command = ["gda", "search"]

    # Get dork type
    search_type = get_search_type()
    if search_type == "single":
        dork = get_dork_from_user()
        command.extend(["--query", dork])
    else:
        template = get_template_from_user()
        command.extend(["--template", template])

    # Get backend
    backend = get_backend()
    command.append(f"--{backend}")

    # Get output file
    output_file = get_output_file()
    extension = Path(output_file).suffix

    if extension == ".csv":
        command.extend(["--output-csv", output_file])
    elif extension == ".jsonl":
        command.extend(["--output-jsonl", output_file])
    elif extension in [".db", ".sqlite", ".sqlite3"]:
        command.extend(["--output-sqlite", output_file])
    elif extension == ".xlsx":
        command.extend(["--output-excel", output_file])
    else:
        console.print(f"[yellow]Warning: Unknown file extension '{extension}'. No output will be saved.[/yellow]")

    console.print("\n" + Panel(
        f"Ready to run the following command:\n\n[bold white]{' '.join(command)}[/bold white]",
        title="[bold cyan]Execution Plan[/bold cyan]",
        border_style="cyan"
    ))

    run = Prompt.ask("Do you want to proceed?", choices=["y", "n"], default="y")
    if run == "y":
        console.print("\n[green]Executing...[/green]\n")
        # Use python -m to ensure we're running from the right context
        process = subprocess.run(["python", "-m", "google_dork_automation.cli"] + command[1:], capture_output=True, text=True)

        console.print("[bold]--- Tool Output ---[/bold]")
        console.print(process.stdout)
        if process.stderr:
            console.print("[bold red]--- Errors ---[/bold red]")
            console.print(process.stderr)
        console.print("[bold]--- End of Output ---[/bold]")
    else:
        console.print("\n[yellow]Aborted.[/yellow]")

if __name__ == "__main__":
    main()
