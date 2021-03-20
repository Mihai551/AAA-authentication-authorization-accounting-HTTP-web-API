import mysql
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    auth_plugin='mysql_native_password',
    database = "database"
)

mycursor = db.cursor()
db.commit()

class user():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.authorization = 0

    def get_authorization(self):
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM table1")
        records = mycursor.fetchall()
        for row in records:
            if row[0] == self.username:
                self.authorization = row[2]


def user_match(username):
    x = False
    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM table1;")
    records = mycursor.fetchall()
    for row in records:
        if row[0] == username:
            x = True
            break
    db.commit()
    return x

def match(username, password):
    x = False
    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM table1;")
    records = mycursor.fetchall()
    for row in records:
        if row[0] == username and row[1] == password:
            x = True
            break
    db.commit()
    return x


def authorize(list):
    for user in list:
        return user.authorization

def log (list, service):
    #time = datetime.now().day.__str__() +'.'+ datetime.now().month.__str__() +'.'+ datetime.now().year.__str__()
    #print(time)
    for user in list:
        mycursor.execute("INSERT INTO log(username, accessed_service, time) VALUES(%s,%s,%s)",
                         (user.username, service, datetime.now()) )
        db.commit()

