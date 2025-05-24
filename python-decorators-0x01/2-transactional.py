
import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function within a transaction
            result = func(conn, *args, **kwargs)
            # Commit the transaction if no errors
            conn.commit()
            return result
        except Exception as e:
            # Rollback the transaction on error
            conn.rollback()
            raise e  # Re-raise the exception for caller to handle
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return cursor.rowcount

# Example: Create a sample database and table for testing
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

# Main execution
if __name__ == "__main__":
    # Set up the database
    setup_database()
    
    # Update user's email with automatic transaction handling
    try:
        rows_affected = update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        print(f"Updated {rows_affected} user(s)")
        
        # Verify the update
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = ?", (1,))
        updated_email = cursor.fetchone()[0]
        print(f"New email for user 1: {updated_email}")
        conn.close()
    except Exception as e:
        print(f"Error updating email: {e}")
