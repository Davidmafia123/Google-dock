import aiosqlite
from pathlib import Path
from typing import List, Optional

from ..core.models import SearchResult

class SqliteStorage:
    """Handles storage of search results in a SQLite database."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def _get_connection(self) -> aiosqlite.Connection:
        """Establishes and returns the database connection."""
        if self._connection is None:
            # Ensure the directory for the database file exists.
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = await aiosqlite.connect(self.db_path)
        return self._connection

    async def init_db(self):
        """Initializes the database and creates the results table if it doesn't exist."""
        conn = await self._get_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                snippet TEXT NOT NULL
            )
        """)
        await conn.commit()
        print(f"Database initialized at {self.db_path}")

    async def save_results(self, results: List[SearchResult]):
        """
        Saves a list of search results to the database.
        Duplicates (based on URL) are ignored due to the UNIQUE constraint.
        """
        if not results:
            return

        conn = await self._get_connection()
        data_to_insert = [
            (res.timestamp.isoformat(), res.title, str(res.url), res.snippet)
            for res in results
        ]

        try:
            await conn.executemany(
                "INSERT OR IGNORE INTO results (timestamp, title, url, snippet) VALUES (?, ?, ?, ?)",
                data_to_insert
            )
            await conn.commit()

            # To get the actual number of inserted rows, we can check changes.
            # This is a bit more complex, so for now, we'll just report success.
            cursor = await conn.cursor()
            await cursor.execute("SELECT changes()")
            changes = (await cursor.fetchone())[0]

            print(f"Saved {changes} new results to {self.db_path} ({len(data_to_insert) - changes} duplicates ignored).")

        except aiosqlite.Error as e:
            print(f"An error occurred while saving to SQLite: {e}")

    async def close(self):
        """Closes the database connection if it's open."""
        if self._connection:
            await self._connection.close()
            self._connection = None
