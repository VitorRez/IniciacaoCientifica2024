from .db_connector import connect_to_db, create_random_string
from .elections import search_end_setting, search_end_election
from mysql.connector import Error, IntegrityError
from datetime import datetime
from Crypto.Random import get_random_bytes
from crypto.CryptoUtils.hash import *
import json
import random

def create_credential(electionid):
    db = connect_to_db()

    try:
        credential = create_random_string(256).encode()
        salt = get_random_bytes(16)

        db.cursor().execute("INSERT INTO CREDENTIALS (CREDENTIAL, ELECTIONID, SALT) VALUES (%s, %s, %s);", (credential, electionid, salt))
        db.commit()
        db.close()
        return {"success": True, "data": "credential successfully created"}
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "credential already exists."}
        
        else:
            return {"success": False, "error": str(e)}
        
        
def get_commits(electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT CREDENTIAL, SALT FROM CREDENTIALS WHERE ELECTIONID = %s;", (electionid,))
        rows = cursor.fetchall()
        db.close()

        commits = []
        for cred, salt in rows:
            commit = create_hash((cred + salt))
            commits.append(commit)

        return {"success": True, "data": commits}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


def get_random_credential(electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()

        # Seleciona credenciais disponíveis (não utilizadas)
        cursor.execute("SELECT CREDENTIAL FROM CREDENTIALS WHERE ELECTIONID = %s AND USED = FALSE;", (electionid,))
        rows = cursor.fetchall()

        if not rows:
            db.close()
            return {"success": False, "error": "No available credentials"}

        # Escolhe uma credencial aleatória
        credential = random.choice(rows)[0]

        # Marca a credencial como utilizada
        cursor.execute("UPDATE CREDENTIALS SET USED = 1 WHERE CREDENTIAL = %s AND ELECTIONID = %s;", (credential, electionid))
        db.commit()
        db.close()

        return {"success": True, "data": credential}

    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    
def check_credential_exists(credential, electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM CREDENTIALS WHERE CREDENTIAL = %s AND ELECTIONID = %s;", (credential, electionid))
        count = cursor.fetchone()[0]

        db.close()

        if count > 0:
            return {"success": True, "message": "exist"}
        
        return {"success": False, "error": "does not exist"}
        

    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
