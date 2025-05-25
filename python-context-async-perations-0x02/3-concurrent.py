import asyncio
import aiosqlite
from typing import List, Any, Tuple

class ExecuteQuery:
    """A context manager for executing async SQL queries with aiosqlite."""
    
    def __init__(self, db_name: str, query: str, params: Tuple[Any, ...] = ()):
        """Initialize with database name, query, and optional parameters."""
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None
        self.results: List[Any] = []
    
    async def __aenter__(self) -> List[Any]:
        """Open async connection, execute query, and return results."""
        self.conn = await aiosqlite.connect(self.db_name)
        self.cursor = await self.conn.cursor()
        await self.cursor.execute(self.query, self.params)
        self.results = await self.cursor.fetchall()
        return self.results
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Close cursor and connection, committing changes if no errors."""
        if self.cursor:
            await self.cursor.close()
        if self.conn:
            if exc_type is None:  # Commit only if no exception occurred
                await self.conn.commit()
            await self.conn.close()

async def async_fetch_users() -> List[Any]:
    """Fetch all users from the database."""
    query = "SELECT * FROM users"
    async with ExecuteQuery("example.db", query) as results:
        return results

async def async_fetch_older_users() -> List[Any]:
    """Fetch users older than 40 from the database."""
    query = "SELECT * FROM users WHERE age > ?"
    params = (40,)
    async with ExecuteQuery("example.db", query, params) as results:
        return results

async def fetch_concurrently():
    """Run both queries concurrently and print results."""
    # Use asyncio.gather to run queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
        return_exceptions=True
    )
    
    print("All users:")
    for row in all_users:
        print(row)
    
    print("\nUsers older than 40:")
    for row in older_users:
        print(row)

if __name__ == "__main__":
    # Run the concurrent fetch
    asyncio.run(fetch_concurrently())
