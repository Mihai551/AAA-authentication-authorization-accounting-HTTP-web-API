from flask import Flask, jsonify, request
import mysql.connector
from user import user, match, user_match

app = Flask(__name__)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    auth_plugin='mysql_native_password',
    database = "database"
)

mycursor = db.cursor()
db.commit()



@app.route('/')
def Welcome():

    return "Welcome!"


@app.route('/users')
def users():
    list = []
    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM table1;")
    users = mycursor.fetchall()
    for user in users:
        list.append(user)
    return jsonify(list)


@app.route('/register', methods  = ['POST'] )
def register():

    if user_match(request.get_json()['username']):
        return jsonify('This username is already used')
    else:
        mycursor.execute("INSERT INTO table1(username, password) VALUES(%s,%s)", (request.get_json()['username'], request.get_json()['password']))
        db.commit()
        return jsonify('Successfully registered')



@app.route('/login', methods  = ['POST'] )
def login():
    if match(request.get_json()['username'], request.get_json()['password']):

        current_user = user(request.get_json()['username'], request.get_json()['password'])
        current_user.get_authorization()
        x = {"Successfully logged in":current_user.username,
             "Your authorization is:":current_user.authorization}
        return x
    else:
        return jsonify('Username or password doesn\'t match')

@app.route('/logout', methods  = ['POST'] )
def logout():
    del current_user
    return jsonify('Successfully logged out')


app.run(debug=True)