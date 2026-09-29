import sqlite3
from engine.config import DB_PATH

def init_database():
    """Database va jadvallarni initialize qilish"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # sys_command table
    query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
    cursor.execute(query)
    
    # web_command table
    query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
    cursor.execute(query)
    
    # contacts table
    query = "CREATE TABLE IF NOT EXISTS contacts(id integer primary key, name VARCHAR(100), phone VARCHAR(20), email VARCHAR(100))"
    cursor.execute(query)
    
    # command_history table
    query = "CREATE TABLE IF NOT EXISTS command_history(id integer primary key, command TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(query)
    
    conn.commit()
    
    # Default data qo'shish
    add_default_data(cursor, conn)
    
    conn.close()

def add_default_data(cursor, conn):
    """Default ma'lumotlarni qo'shish"""
    
    # Check sys_command table
    cursor.execute("SELECT COUNT(*) FROM sys_command")
    if cursor.fetchone()[0] == 0:
        sys_commands = [
            (None, 'notepad', 'C:\\Windows\\System32\\notepad.exe'),
            (None, 'calculator', 'C:\\Windows\\System32\\calc.exe'),
            (None, 'paint', 'C:\\Windows\\System32\\mspaint.exe'),
        ]
        cursor.executemany("INSERT INTO sys_command VALUES (?,?,?)", sys_commands)
    
    # Check web_command table
    cursor.execute("SELECT COUNT(*) FROM web_command")
    if cursor.fetchone()[0] == 0:
        web_commands = [
            (None, 'google', 'https://www.google.com/'),
            (None, 'instagram', 'https://www.instagram.com/'),
            (None, 'facebook', 'https://www.facebook.com/'),
            (None, 'youtube', 'https://www.youtube.com/'),
            (None, 'github', 'https://www.github.com/'),
        ]
        cursor.executemany("INSERT INTO web_command VALUES (?,?,?)", web_commands)
    
    conn.commit()

def get_db_connection():
    """Database ulanishni olish"""
    return sqlite3.connect(DB_PATH)




# testing module 

#app_name = "Telegram"
#cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
#results = cursor.fetchall()
#print(results[0][0])










# create a table with the desired columns

#cursor.execute("CREATE TABLE IF NOT EXISTS contants(id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL)")



# Specify the column indices you want to import (0-based index)
# Example: Importing the 1st and 3rd columns
#desired_columns_indices = [0, 30]

# Read data from CSV and insert into SQLite table for the desired columns
#with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         selected_data = [row[i] for i in desired_columns_indices]
#         cursor.execute(" INSERT INTO contants(id, 'name', 'mobile_no') VALUES (null, ?, ?);", tuple(selected_data))

 # Commit changes and close connection
#conn.commit()
#conn.close()



# isim orqali malumotlar bazasidan nomir qidiradi


#query = 'javoxir'
#query = query.strip().lower()

#cursor.execute("SELECT mobile_no FROM contants WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
#results = cursor.fetchall()
#print(results[0][0])

