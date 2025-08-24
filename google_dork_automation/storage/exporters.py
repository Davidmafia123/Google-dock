import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..core.models import SearchResult

class AbstractExporter(ABC):
    """Abstract base class for result exporters."""

    @abstractmethod
    def write(self, results: List[SearchResult], filepath: Path):
        """
        Writes the search results to a file.

        Args:
            results: A list of SearchResult objects.
            filepath: The path to the output file.
        """
        pass

class CsvExporter(AbstractExporter):
    """Exports search results to a CSV file."""

    def write(self, results: List[SearchResult], filepath: Path):
        """Writes results to a CSV file with a header."""
        if not results:
            return

        # Ensure the directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        header = ["timestamp", "title", "url", "snippet"]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for result in results:
                writer.writerow([
                    result.timestamp.isoformat(),
                    result.title,
                    str(result.url),
                    result.snippet
                ])
        print(f"Successfully exported {len(results)} results to {filepath}")

class JsonLinesExporter(AbstractExporter):
    """Exports search results to a JSON-Lines (.jsonl) file."""

    def write(self, results: List[SearchResult], filepath: Path):
        """Writes each result as a JSON object on a new line."""
        if not results:
            return

        # Ensure the directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            for result in results:
                f.write(result.model_dump_json() + "\n")
        print(f"Successfully exported {len(results)} results to {filepath}")

class ExcelExporter(AbstractExporter):
    """Exports search results to an Excel (.xlsx) file."""

    def write(self, results: List[SearchResult], filepath: Path):
        """Writes results to an Excel file."""
        if not results:
            return

        import pandas as pd

        # Ensure the directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Convert list of Pydantic models to a list of dicts
        data = [result.model_dump(mode='json') for result in results]

        # Create a pandas DataFrame
        df = pd.DataFrame(data)

        # Reorder columns to be consistent with CSV
        df = df[["timestamp", "title", "url", "snippet"]]

        # Write to Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        print(f"Successfully exported {len(results)} results to {filepath}")
