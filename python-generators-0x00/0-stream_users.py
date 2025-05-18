import mysql.connector
from mysql.connector import Error

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",  # Replace with your MySQL username
            password="your_password",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        if connection.is_connected():
            print("Successfully connected to ALX_prodev database")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def stream_users():
    """Generator to stream rows from user_data table one by one."""
    connection = connect_to_prodev()
    if not connection:
        return

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        # Single loop to yield each row
        for row in cursor:
            yield row
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error streaming rows: {e}")
        if connection.is_connected():
            connection.close()

def main():
    """Demonstrate streaming users."""
    print("\nStreaming users from user_data table:")
    for user in stream_users():
        print(user)

if __name__ == "__main__":
    main()
