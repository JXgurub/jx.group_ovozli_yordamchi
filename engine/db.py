import csv
import sqlite3


conn = sqlite3.connect("jarvis.db")

cursor = conn.cursor()




#query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
#cursor.execute(query)



#query = "INSERT INTO sys_command VALUES (null,'android studio', 'C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe')"
#cursor.execute(query)
#conn.commit()





query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)



# bu yerda malumotlar bazasiga sayt linklari qo'shiladi


query = "INSERT INTO web_command VALUES (null,'instagram', 'https://www.instagram.com/')"
cursor.execute(query)
conn.commit()






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

