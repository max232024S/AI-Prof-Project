import sqlite3
connect = sqlite3.connect('../ai_prof.db')
cursor = connect.cursor()

#test file for viewing data inside of database

    
try:
    with connect:
        while True:
            command = input('Enter your SQL query command\n')
            if command == 'exit':
                break
            
            cursor.execute(command)
            print(cursor.fetchall())
finally:
    connect.close()

