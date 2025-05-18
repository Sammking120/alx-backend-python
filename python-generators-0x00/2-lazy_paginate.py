
import mysql.connector
from mysql.connector import Error

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="sammking",  # Replace with your MySQL username
            password="passdem",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        if connection.is_connected():
            print("Successfully connected to ALX_prodev database")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def paginate_users(page_size, offset):
    """Fetch a specific page of users from user_data table."""
    connection = connect_to_prodev()
    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Error as e:
        print(f"Error fetching page: {e}")
        if connection.is_connected():
            connection.close()
        return []

def lazy_paginate(page_size):
    """Generator to lazily load pages of users starting at offset 0."""
    offset = 0
    # Single loop to fetch pages
    while True:
        page = paginate_users(page_size, offset)
        if not page:  # No more data to fetch
            break
        yield page
        offset += page_size

def main():
    page_size = 2  # Example page size
    print(f"\nLazily paginating users with page size {page_size}:")
    # Iterate over pages
    for page in lazy_paginate(page_size):
        print("Page:", page)

if __name__ == "__main__":
    main()
