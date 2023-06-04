import mysql.connector 
from app import db  

# Connect to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="327baf2bcf1c1bc4ba3fbb5a9b95e69db7b1e61222e12c04bbd5e5a5d8a3676c"
)


my_cursor=mydb.cursor()
my_cursor.execute("SHOW DATABASES")


# Check if database already exists
# else create it

usersExist=False
for db in my_cursor:
    if(db[0]=="users"):
        usersExist=True
        print("Database already exists") 
        
if(usersExist==False):
    my_cursor.execute("CREATE DATABASE users")
    print("Database 'USERS' created")


# Connect to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="327baf2bcf1c1bc4ba3fbb5a9b95e69db7b1e61222e12c04bbd5e5a5d8a3676c",
    database="users"
)



for i in range(15):
    add_employee = ("INSERT INTO Relays "
               "(state, DateTime) "
               "VALUES (%b, %d)")

my_cursor.close()