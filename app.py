from flask import Flask, jsonify, request
import mysql.connector
from user import user, user_match, match, authorize, log

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
store_current_user = []


@app.route('/')
def Welcome():

    return "Welcome!"


@app.route('/users')
def users():
    if authorize(store_current_user):
        log(store_current_user,'users')
        list = []
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM table1;")
        users = mycursor.fetchall()
        for user in users:
            list.append(user)
        return jsonify(list)
    else:
        return jsonify("You don't have access")


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
    if store_current_user.__len__() > 0:
        return jsonify('You are already logged in')

    if match(request.get_json()['username'], request.get_json()['password']):
        current_user = user(request.get_json()['username'], request.get_json()['password'])
        current_user.get_authorization()
        store_current_user.append(current_user)
        log(store_current_user, 'login')
        print(store_current_user) #for check
        return {"Successfully logged in":current_user.username,
             "Your authorization is:":current_user.authorization}
    else:
        return jsonify('Username or password doesn\'t match')



@app.route('/logout', methods  = ['GET'] )
def logout():
    log(store_current_user, 'logout')
    if store_current_user.__len__() !=0:
        store_current_user.pop()
        print(store_current_user) #for check
        return jsonify('Successfully logged out')
    else:
        return jsonify('You are not logged in')


@app.route('/logs', methods  = ['GET'] )
def logs():
    if authorize(store_current_user):

        list = []
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM log;")
        records = mycursor.fetchall()
        for logs in records:
            list.append(logs)
        log(store_current_user, 'logs')
        return jsonify(list)
    else:
        return jsonify("You don't have access")


app.run(debug=True)