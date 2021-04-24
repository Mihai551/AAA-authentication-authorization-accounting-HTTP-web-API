from flask import Flask, jsonify, request, #redirect, url_for
import mysql.connector
from user import *
from flask_mail import Mail, Message
from random_string import get_random_string


app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mihai.api.mails@gmail.com'
app.config['MAIL_PASSWORD'] = '**********'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
store_email_for_recovery = []
store_recovery_code=[]

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
    if email_address_match(request.get_json()['email_address'], mycursor,'table1', db):
        return jsonify('This email address is already used')
    if user_match(request.get_json()['username'], mycursor,'table1', db):
        return jsonify('This username is already used')
    else:
        mycursor.execute("INSERT INTO table1(username, password, email_address) VALUES(%s,%s,%s)",
                         (request.get_json()['username'], request.get_json()['password'], request.get_json()['email_address']))
        db.commit()

        current_user = user(request.get_json()['email_address'], request.get_json()['username'], request.get_json()['password'])
        current_user.get_authorization(mycursor, 'table1', db)
        store_current_user.append(current_user)
        log(store_current_user, 'register', mycursor, 'log', db)

        msg = Message('Registration', sender='mihai.api.mails@gmail.com', recipients=[current_user.email_address])
        msg.body = (f"Hello {current_user.username},\n\nYour account was successfully created!\n\nAPI team")
        mail.send(msg)

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
    """UNBAN IP addresses"""
    if authorize(store_current_user):
        if row_from_table('IP', request.get_json()['IP'], mycursor, 'banned_ip_addresses', db):
            delete_row('IP', request.get_json()['IP'], mycursor, 'banned_ip_addresses', db)
            log(store_current_user, 'unban_ip', mycursor, 'log', db)
            return jsonify("IP address successfully unbanned")
        else:
            return jsonify("IP address can't be found")

    else:
        return jsonify("You don't have access")


@app.route('/get_recovery_code', methods  = ['POST'] )
def get_code():
    """Send an email that contains the account recovery code"""
    if row_from_table(column='email_address', variable=request.get_json()['email_address'], mycursor=mycursor, table='table1', db=db):
        recovery_code = get_random_string(15)
        store_recovery_code.append(recovery_code)
        print(recovery_code)
        store_email_for_recovery.append(request.get_json()['email_address'])
        msg = Message('Account recovery', sender='mihai.api.mails@gmail.com', recipients=[request.get_json()['email_address']])
        msg.body = (f"Hello,\n\nYour account recovery code is {recovery_code} !\n\nAPI team")
        mail.send(msg)
        return jsonify("Recovery code sent")

    else: return jsonify("This email address doesn't exist")


@app.route('/get_new_password', methods  = ['POST'] )
def get_new_password():
    """Change your password using account recovery code"""
    for email_address in store_email_for_recovery:
        print(store_recovery_code[0])
        if (request.get_json()['recovery_code'] == store_recovery_code[0]):
            if (request.get_json()['new password'] == request.get_json()['confirm new password']):
                change(column_to_find = 'email_address', attribute_to_find=email_address, column_to_change = 'password',
                       attribute_to_change = request.get_json()['new password'], mycursor = mycursor, table = 'table1', db=db)
                store_email_for_recovery.pop()
                store_recovery_code.pop()
                return jsonify("Password successfully changed. Please log in.")

            else:
                store_email_for_recovery.pop()
                return jsonify("'new password' and 'confirm new password' must match")

        else:
            store_email_for_recovery.pop()
            store_recovery_code.pop()
            return  jsonify("The account recovery code doesn't match")

    return jsonify("You need to introduce your email address")







app.run(debug=True)
