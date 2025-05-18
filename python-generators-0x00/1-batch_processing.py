
import mysql.connector
from mysql.connector import Error

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host ="localhost",
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

def stream_users_in_batches(batch_size):
    """Generator to fetch rows from user_data table in batches."""
    connection = connect_to_prodev()
    if not connection:
        return

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        # Loop 1: Fetch rows in batches
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error streaming batches: {e}")
        if connection.is_connected():
            connection.close()

def batch_processing(batch_size):
    """Process batches to filter users over age 25."""
    # Loop 2: Iterate over batches from generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Filter users in the batch
        filtered_users = [user for user in batch if user['age'] > 25]
        yield filtered_users

def main():
    batch_size = 2  # Example batch size
    print(f"\nProcessing batches of size {batch_size} (users over age 25):")
    # Process and print filtered batches
    for filtered_batch in batch_processing(batch_size):
        print("Batch:", filtered_batch)

if __name__ == "__main__":
    main()
