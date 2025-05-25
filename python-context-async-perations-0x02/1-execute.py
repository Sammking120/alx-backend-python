import sqlite3
from typing import Optional, Tuple, Any, List

class ExecuteQuery:
    """A context manager for executing SQL queries with parameters."""
    
    def __init__(self, db_name: str, query: str, params: Tuple[Any, ...] = ()):
        """Initialize with database name, query, and optional parameters."""
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.results: List[Any] = []
    
    def __enter__(self) -> List[Any]:
        """Open connection, execute query, and return results."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close cursor and connection, committing changes if no errors."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:  # Commit only if no exception occurred
                self.conn.commit()
            self.conn.close()

# Example usage with the specified query
if __name__ == "__main__":
    # Assuming a SQLite database 'example.db' with a 'users' table
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    with ExecuteQuery("example.db", query, params) as results:
        for row in results:
            print(row)
