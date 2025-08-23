import yaml
from importlib import resources
from typing import Dict, Any
import rich

def load_templates() -> Dict[str, Any]:
    """
    Loads the dork templates from the packaged YAML file.

    Returns:
        A dictionary containing the parsed template data, or an empty dictionary on error.
    """
    try:
        # According to the docs, for Python 3.9+ this is the way to get a path-like object
        # to a resource inside a package.
        template_file_path = resources.files('google_dork_automation.resources').joinpath('dork_templates.yaml')
        with template_file_path.open('r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
            return templates if templates else {}
    except (FileNotFoundError, yaml.YAMLError) as e:
        rich.print(f"[bold red]Error loading dork templates: {e}[/bold red]")
        return {}
    except Exception as e:
        # Catch other potential errors, like ModuleNotFoundError if package is structured unexpectedly
        rich.print(f"[bold red]An unexpected error occurred while loading dork templates: {e}[/bold red]")
        return {}
