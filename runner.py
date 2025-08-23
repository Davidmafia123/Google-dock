#!/usr/bin/env python
"""
A simple runner script for development.
This allows running the CLI without installing the package.
"""

import sys
from pathlib import Path

# Add the project root to the path to allow imports from the package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from google_dork_automation.cli import app

if __name__ == "__main__":
    app()
