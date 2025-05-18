
import mysql.connector
import csv
import uuid
from mysql.connector import Error

def connect_db():
    """Connect to the MySQL database server."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="sammking",  # Replace with your MySQL username
            password="passdem"  # Replace with your MySQL password
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Create the ALX_prodev database if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

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

def create_table(connection):
    """Create the user_data table if it does not exist."""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, data):
    """Insert data into the user_data table if it does not exist."""
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        # Check for existing user_id to avoid duplicates
        check_query = "SELECT user_id FROM user_data WHERE user_id = %s"
        
        for row in data:
            user_id = row['user_id'] if row['user_id'] else str(uuid.uuid4())
            cursor.execute(check_query, (user_id,))
            if cursor.fetchone() is None:
                cursor.execute(insert_query, (user_id, row['name'], row['email'], row['age']))
                print(f"Inserted data for {row['name']}")
            else:
                print(f"Data for user_id {user_id} already exists, skipping")
        
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")

def stream_rows(connection):
    """Generator to stream rows from user_data table one by one."""
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        for row in cursor:
            yield row
        cursor.close()
    except Error as e:
        print(f"Error streaming rows: {e}")

def main():
    # Connect to MySQL server
    connection = connect_db()
    if not connection:
        return
    
    # Create database
    create_database(connection)
    connection.close()
    
    # Connect to ALX_prodev database
    connection = connect_to_prodev()
    if not connection:
        return
    
    # Create table
    create_table(connection)
    
    # Read sample CSV data
    csv_file = "user_data.csv"
    data = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Ensure age is a float
                row['age'] = float(row['age'])
                data.append(row)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found")
        connection.close()
        return
    
    # Insert data
    insert_data(connection, data)
    
    # Stream and print rows
    print("\nStreaming rows from user_data table:")
    for row in stream_rows(connection):
        print(row)
    
    # Close connection
    connection.close()

if __name__ == "__main__":
    main()
