from datetime import datetime
from flask import jsonify


class user():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.authorization = 0

    def get_authorization(self, mycursor, table, db):
        for row in rows_from_table(mycursor, table, db):
            if row[0] == self.username:
                self.authorization = row[2]


def access(store_current_user,service, mycursor, logs_table, table_to_read, db):

    """Returns a table as a jesonified list"""

    if authorize(store_current_user):
        log(store_current_user,service, mycursor, logs_table, db)
        list = []
        for row in rows_from_table(mycursor, table_to_read, db):
            list.append(row)
        return jsonify(list)
    else:
        return jsonify("You don't have access")


def rows_from_table(mycursor, table, db):

    """Returns the rows of a table"""

    mycursor.execute(f"SELECT * FROM {table};")
    records = mycursor.fetchall()
    db.commit()
    return records


def row_from_table(column, variable, mycursor, table, db):

    """Returns the rows of a table"""

    mycursor.execute(f"SELECT * FROM {table} WHERE {column} LIKE '%{variable}%';")
    records = mycursor.fetchall()
    db.commit()
    return records

def user_match(username, mycursor, table, db):
    """Checks if the username is already used"""
    x = False
    for row in row_from_table('username', username ,mycursor, table ,db):
        if row[0] == username:
            x = True
            break
    db.commit()
    return x


def match(username, password, mycursor, table, db):
    """Checks if username and password match"""
    x = False

    for row in row_from_table('username', username, mycursor, table ,db):
        if row[0] == username and row[1] == password:
            x = True
            break
    db.commit()
    return x


def authorize(list):
    """Returns the authorization of the current user"""
    for user in list:
        return user.authorization

def log (list, service, mycursor, table, db):
    """Records the actions"""
    for user in list:

        mycursor.execute(f"INSERT INTO {table}(username, accessed_service, time) VALUES(%s,%s,%s)",
                         (user.username, service, datetime.now()) )
        db.commit()