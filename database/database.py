import sqlite3

conn = sqlite3.connect('ai_prof.db')

cursor = conn.cursor()

with open('schema.sql', 'r') as f:
    sql_script = f.read()
    
cursor.executescript(sql_script)
conn.commit()
conn.close()