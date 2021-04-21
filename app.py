from flask import Flask, jsonify, request
import mysql.connector
from user import *

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

        current_user = user(request.get_json()['username'], request.get_json()['password'])
        current_user.get_authorization(mycursor, 'table1', db)
        store_current_user.append(current_user)
        log(store_current_user, 'register', mycursor, 'log', db)

        return jsonify('Successfully registered')



@app.route('/login', methods  = ['POST'] )
def login():
    """Login"""
    if store_current_user.__len__() > 0:
        return jsonify('You are already logged in')

    if row_from_table('IP', get('https://api.ipify.org').text, mycursor, 'banned_ip_addresses', db):
        return jsonify('This IP is banned')
    else:
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

@app.route('/change_password', methods  = ['POST'] )
def change_password():
    """Change your password"""
    if store_current_user.__len__():
        for user in store_current_user:
            if request.get_json()['password']==user.password and request.get_json()['new password'] == request.get_json()['confirm new password']:
                user.password = request.get_json()['new password']
                change(column_to_find='username', attribute_to_find=user.username, column_to_change='password', attribute_to_change=user.password, mycursor=mycursor, table='table1', db=db)
                log(store_current_user,'change_password', mycursor, 'log', db)
                return jsonify('Your password was successfully changed')

            elif request.get_json()['password']!=user.password:
                return jsonify('Wrong password')

            elif request.get_json()['new password'] != request.get_json()['confirm new password']:
                return jsonify("'new password' and 'confirm new password' must match")
    else:
        return  jsonify('You are not logged in' )


@app.route('/ban_ip', methods  = ['POST'] )
def ban_ip():
    """BAN IP addresses"""
    if authorize(store_current_user):
        if row_from_table('IP', request.get_json()['IP'], mycursor, 'banned_ip_addresses', db):
            return jsonify("This IP is already banned")
        else:
            mycursor.execute("INSERT INTO banned_ip_addresses(IP) VALUES ('"+request.get_json()['IP']+"');")
            db.commit()
            log(store_current_user, 'ban_ip', mycursor, 'log', db)
            return jsonify("IP address successfully banned")

    else:
        return jsonify("You don't have access")


@app.route('/unban_ip', methods  = ['POST'] )
def unban_ip():
    if authorize(store_current_user):
        if row_from_table('IP', request.get_json()['IP'], mycursor, 'banned_ip_addresses', db):
            delete_row('IP', request.get_json()['IP'], mycursor, 'banned_ip_addresses', db)
            log(store_current_user, 'unban_ip', mycursor, 'log', db)
            return jsonify("IP address successfully unbanned")
        else:
            return jsonify("IP address can't be found")

    else:
        return jsonify("You don't have access")

app.run(debug=True)
