import pytest
from pathlib import Path
from datetime import datetime, timezone

from google_dork_automation.core.models import SearchResult
from google_dork_automation.storage.sqlite import SqliteStorage

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
            title="Result 2",
            url="https://example.com/2",
            snippet="This is snippet 2.",
            timestamp=datetime(2023, 1, 1, 12, 0, 1, tzinfo=timezone.utc),
        ),
    ]

@pytest.mark.asyncio
async def test_sqlite_storage_save_and_retrieve(sample_results):
    """Tests initializing the DB, saving results, and verifies the data."""
    # Use an in-memory database for testing
    storage = SqliteStorage(db_path=Path(":memory:"))
    await storage.init_db()

    await storage.save_results(sample_results)

    # Verify the data was inserted correctly
    conn = await storage._get_connection()
    cursor = await conn.execute("SELECT timestamp, title, url, snippet FROM results ORDER BY url")
    rows = await cursor.fetchall()

    assert len(rows) == 2
    assert rows[0][2] == "https://example.com/1"
    assert rows[0][1] == "Result 1"
    assert rows[1][2] == "https://example.com/2"
    assert rows[1][1] == "Result 2"

    await storage.close()

@pytest.mark.asyncio
async def test_sqlite_deduplication(sample_results):
    """Tests that duplicate URLs are not saved."""
    storage = SqliteStorage(db_path=Path(":memory:"))
    await storage.init_db()

    # Save the results for the first time
    await storage.save_results(sample_results)

    conn = await storage._get_connection()
    cursor = await conn.execute("SELECT COUNT(*) FROM results")
    count1 = (await cursor.fetchone())[0]
    assert count1 == 2

    # Add a new result and a duplicate one
    new_results = [
        sample_results[0], # Duplicate of Result 1
        SearchResult(
            title="Result 3",
            url="https://example.com/3",
            snippet="This is snippet 3.",
            timestamp=datetime.now(timezone.utc)
        )
    ]

    # Save again
    await storage.save_results(new_results)

    cursor = await conn.execute("SELECT COUNT(*) FROM results")
    count2 = (await cursor.fetchone())[0]

    # The count should only increase by 1 (for Result 3)
    assert count2 == 3

    await storage.close()
