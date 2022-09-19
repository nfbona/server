import mysql.connector 

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="327baf2bcf1c1bc4ba3fbb5a9b95e69db7b1e61222e12c04bbd5e5a5d8a3676c",
)

my_cursor=mydb.cursor()

my_cursor.execute("CREATE DATABASE users")
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)