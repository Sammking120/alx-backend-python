
import sqlite3
import functools
import logging
import datetime

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the query from the first argument
        query = args[0] if args else kwargs.get('query', '')
        # Log the query with timestamp
        logging.info(f"Executing query: {query}")
        # Execute the original function
        result = func(*args, **kwargs)
        return result
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

    #### fetch users while logging the query
if __name__ == "__main__":
    query = "SELECT * FROM users"
    users = fetch_all_users(query="SELECT * FROM users")
    for user in users:
        print(user)
