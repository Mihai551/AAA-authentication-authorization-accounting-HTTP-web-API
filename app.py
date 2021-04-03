from flask import Flask, jsonify, request
import mysql.connector
from user import user, user_match, match, log, access

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
    """Returns the list of users"""
    return access(store_current_user,'users', mycursor, 'log', 'table1', db)


@app.route('/register', methods  = ['POST'] )
def register():
    """Register"""
    if user_match(request.get_json()['username'], mycursor,'table1', db):
        return jsonify('This username is already used')
    else:
        mycursor.execute("INSERT INTO table1(username, password) VALUES(%s,%s)", (request.get_json()['username'], request.get_json()['password']))
        db.commit()
        return jsonify('Successfully registered')



@app.route('/login', methods  = ['POST'] )
def login():
    """Login"""
    if store_current_user.__len__() > 0:
        return jsonify('You are already logged in')

    if match(request.get_json()['username'], request.get_json()['password'], mycursor,'table1', db):
        current_user = user(request.get_json()['username'], request.get_json()['password'])
        current_user.get_authorization(mycursor, 'table1', db)
        store_current_user.append(current_user)
        log(store_current_user, 'login', mycursor, 'log', db)
        return {"Successfully logged in":current_user.username,
             "Your authorization is:":current_user.authorization}
    else:
        return jsonify('Username or password doesn\'t match')



@app.route('/logout', methods  = ['GET'] )
def logout():
    """Logout"""
    log(store_current_user, 'logout', mycursor, 'log', db)
    if store_current_user.__len__() !=0:
        store_current_user.pop()
        return jsonify('Successfully logged out')
    else:
        return jsonify('You are not logged in')


@app.route('/logs', methods  = ['GET'] )
def logs():
    """Returns logs list"""
    return access(store_current_user,'logs', mycursor, 'log', 'log', db)


app.run(debug=True)
