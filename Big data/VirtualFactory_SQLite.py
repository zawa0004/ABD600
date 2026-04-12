import sqlite3
import time
import random
from datetime import datetime

def create_tables():
    try:
        connection = sqlite3.connect('bigdata.db')
        cursor = connection.cursor()
        
        # Create battery_status table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS battery_status (
                Record_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Measurement_Time DATETIME NOT NULL,
                Location TEXT NOT NULL,
                Battery INTEGER NOT NULL
            )
        ''')
        
        # Create environmental_conditions table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environmental_conditions (
                Record_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Measurement_Time DATETIME,
                Location TEXT,
                Temperature REAL,
                Humidity REAL,
                Damaged INTEGER
            )
        ''')
        
        connection.commit()
        print("Tables created or verified successfully.")
    except sqlite3.Error as error:
        print(f"Error while creating tables: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def call_generate_environmental_conditions():
    try:
        # Connect to the SQLite database file
        connection = sqlite3.connect('bigdata.db')
        cursor = connection.cursor()

        # Randomly choose a location from a, b, c, or d.
        location = random.choice(['a', 'b', 'c', 'd'])
        
        # Generate random temperature between 20 and 35 (float with one decimal).
        temperature = round(random.uniform(20, 35), 1)
        
        # Generate random humidity between 30 and 100 (integer).
        humidity = random.randint(30, 100)
        
        # Determine if damage occurs; True (1) for ~10% of cases.
        damaged = 1 if random.random() < 0.10 else 0
        
        # Get the current time.
        measurement_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert the generated record into the environmental_conditions table.
        cursor.execute(
            "INSERT INTO environmental_conditions (Measurement_Time, Location, Temperature, Humidity, Damaged) VALUES (?, ?, ?, ?, ?)", 
            (measurement_time, location, temperature, humidity, damaged)
        )
        connection.commit()
        print(f"Record added: Time={measurement_time}, Location={location}, Temp={temperature}, Humidity={humidity}, Damaged={damaged}")
    except sqlite3.Error as error:
        print(f"Failed to execute simulated procedure: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def clear_sqlite_table(table_name):
    try:
        connection = sqlite3.connect('bigdata.db')
        cursor = connection.cursor()
        
        # Delete all rows from the table
        sql_delete_query = f"DELETE FROM {table_name}"
        cursor.execute(sql_delete_query)
        connection.commit()
        print(f"All records from {table_name} have been deleted successfully.")
    except sqlite3.Error as error:
        print(f"Failed to delete records from SQLite table: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("SQLite connection is closed")

# Create tables if they do not exist
create_tables()

# Clear the environmental_conditions table before starting the loop
clear_sqlite_table('environmental_conditions')

while True:
    call_generate_environmental_conditions()
    time.sleep(1)
