import mysql

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
    return x