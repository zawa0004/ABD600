import sqlite3
conn = sqlite3.connect('bigdata.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM battery_status ORDER BY Record_ID DESC LIMIT 10")
for row in cursor.fetchall():
    print(row)
conn.close()