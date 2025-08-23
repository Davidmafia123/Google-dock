import pytest
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

from google_dork_automation.core.models import SearchResult
from google_dork_automation.storage.exporters import CsvExporter, JsonLinesExporter

@pytest.fixture
def sample_results():
    """Provides a sample list of SearchResult objects for testing."""
    return [
        SearchResult(
            title="Result 1",
            url="https://example.com/1",
            snippet="This is snippet 1.",
            timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        ),
        SearchResult(
            title="Result 2, with comma",
            url="https://example.com/2",
            snippet="This is snippet 2.",
            timestamp=datetime(2023, 1, 1, 12, 0, 1, tzinfo=timezone.utc),
        ),
    ]

def test_csv_exporter(sample_results, tmp_path: Path):
    """Tests writing results to a CSV file."""
    exporter = CsvExporter()
    filepath = tmp_path / "results.csv"

    exporter.write(sample_results, filepath)

    assert filepath.exists()

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["timestamp", "title", "url", "snippet"]

        row1 = next(reader)
        assert row1 == [
            "2023-01-01T12:00:00+00:00",
            "Result 1",
            "https://example.com/1",
            "This is snippet 1.",
        ]

        row2 = next(reader)
        assert row2 == [
            "2023-01-01T12:00:01+00:00",
            "Result 2, with comma",
            "https://example.com/2",
            "This is snippet 2.",
        ]

def test_jsonlines_exporter(sample_results, tmp_path: Path):
    """Tests writing results to a JSON-Lines file."""
    exporter = JsonLinesExporter()
    filepath = tmp_path / "results.jsonl"

    exporter.write(sample_results, filepath)

    assert filepath.exists()

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 2

    data1 = json.loads(lines[0])
    assert data1["title"] == "Result 1"
    assert data1["url"] == "https://example.com/1"
    assert data1["timestamp"] == "2023-01-01T12:00:00Z"

    data2 = json.loads(lines[1])
    assert data2["title"] == "Result 2, with comma"
    assert data2["url"] == "https://example.com/2"
    assert data2["timestamp"] == "2023-01-01T12:00:01Z"

def test_exporter_no_results(tmp_path: Path):
    """Tests that no file is created when there are no results."""
    csv_exporter = CsvExporter()
    jsonl_exporter = JsonLinesExporter()
    csv_filepath = tmp_path / "no_results.csv"
    jsonl_filepath = tmp_path / "no_results.jsonl"

    csv_exporter.write([], csv_filepath)
    jsonl_exporter.write([], jsonl_filepath)

    assert not csv_filepath.exists()
    assert not jsonl_filepath.exists()
