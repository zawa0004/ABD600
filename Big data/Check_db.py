import sqlite3

connection = sqlite3.connect("bigdata.db")
cursor = connection.cursor()

query = """
SELECT Record_ID, Measurement_Time, Location, Battery
FROM battery_status
ORDER BY Record_ID DESC
LIMIT 10
"""

cursor.execute(query)

rows = cursor.fetchall()

print("Last 10 AGV stops from database:\n")

for row in rows:
    print(row)

cursor.close()
connection.close()
