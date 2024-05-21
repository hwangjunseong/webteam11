import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    port="3307",
    user="root",
    password="wktong6877",
    # database="our_users_database"
)
my_cursor = mydb.cursor()
#이건 한번만 실행 후 주석
# my_cursor.execute("CREATE DATABASE our_users_database")
# my_cursor.execute("CREATE DATABASE IF NOT EXISTS our_users")
my_cursor.execute("SHOW DATABASE")
for db in my_cursor:
    print(db)