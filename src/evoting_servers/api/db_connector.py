import mysql.connector
import string
import random

def connect_to_db():
    db = mysql.connector.connect(
        host="192.168.56.10",
        user="ELECTIONAUTH",
        password="Fr468vj#",
        database="evoting_database",
        auth_plugin='mysql_native_password'
    )
    return db

def create_random_string(size):
    s = string.ascii_uppercase + string.digits
    return ''.join(random.choices(s, k=size))