import sqlite3
from typing import Optional

class DatabaseConnection:
    """A context manager for handling SQLite database connections."""
    
    def __init__(self, db_name: str):
        """Initialize with the database name."""
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def __enter__(self):
        """Open the database connection and return the cursor."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Close the cursor and connection, committing changes if no errors."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:  # Commit only if no exception occurred
                self.conn.commit()
            self.conn.close()

# Example usage with a sample database
if __name__ == "__main__":
    # Assuming a SQLite database '' with a 'users' table
    with DatabaseConnection("example.db") as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        for row in results:
            print(row)
