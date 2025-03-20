from .db_connector import connect_to_db, create_random_string
from .elections import search_end_setting, search_end_election
from mysql.connector import Error, IntegrityError
from datetime import datetime
import json

def create_user(username, name, password, is_staff):
    db = connect_to_db()

    try:
        db.cursor().execute("INSERT INTO USERS (USERNAME, NAME, PASSWORD, IS_STAFF) VALUES (%s,%s,%s,%s);", (username, name, password, is_staff))
        db.commit()
        db.close()
        return {"success": True, "message": "user successfully created."}

    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "user already exists."}
        
        else:
            return {"success": False, "error": str(e)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
        
        
def get_users():
    db = connect_to_db()
    
    try:
        cursor = db.cursor()

        cursor.execute("SELECT USERNAME, NAME, PASSWORD, IS_STAFF FROM USERS;")
        rows = cursor.fetchall()
        
        users = [
            {
                "username": row[0],
                "name": row[1],
                "password": row[2],
                "is_staff": row[3]
            }
            for row in rows
        ]

        return {"success": True, "data": users}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    
def get_user(username):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT USERNAME, NAME, PASSWORD, IS_STAFF FROM USERS WHERE USERNAME = %s;", (username,))
        row = cursor.fetchone()
        db.close()

        user = {"username": row[0], "name": row[1], "password": row[2], "is_staff": row[3]}

        if user:
            return {"success": True, "data": user}
        else:
            return {"success": False, "error": "user not found."}
        

    except Exception as e:
        print(2)
        db.close()
        return {"success": False, "error": str(e)}
