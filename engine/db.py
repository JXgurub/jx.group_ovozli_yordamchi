import sqlite3


conn = sqlite3.connect("jarvis.db")

cursor = conn.cursor()




#query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
#cursor.execute(query)



#query = "INSERT INTO sys_command VALUES (null,'android studio', 'C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe')"
#cursor.execute(query)
#conn.commit()





#query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
#cursor.execute(query)

#query = "INSERT INTO web_command VALUES (null,'instagram', 'https://www.instagram.com/')"
#cursor.execute(query)
#conn.commit()




# testing module 

app_name = "Telegram"
cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
results = cursor.fetchall()
print(results[0][0])












