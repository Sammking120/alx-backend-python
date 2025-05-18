
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

def stream_user_ages():
    """Generator to yield user ages one by one."""
    connection = connect_to_prodev()
    if not connection:
        return

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        # Loop 1: Yield each age
        for (age,) in cursor:
            yield float(age)  # Convert Decimal to float for calculations
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error streaming ages: {e}")
        if connection.is_connected():
            connection.close()

def calculate_average_age():
    """Calculate the average age using the generator."""
    total_age = 0.0
    count = 0
    # Loop 2: Iterate over ages from generator
    for age in stream_user_ages():
        total_age += age
        count += 1
    return total_age / count if count > 0 else 0.0

def main():
    try:
        average_age = calculate_average_age()
        print(f"Average age of users: {average_age:.2f}")
    except ZeroDivisionError:
        print("Average age of users: 0.00 (no users found)")

if __name__ == "__main__":
    main()
