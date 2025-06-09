from .db_connector import connect_to_db, create_random_string
from .elections import search_end_setting, search_end_election
from mysql.connector import Error, IntegrityError
from datetime import datetime
from Crypto.Random import get_random_bytes
from crypto.CryptoUtils.hash import *
import json
import random

def create_ballot(electionid, ballot):
    db = connect_to_db()

    try:
        db.cursor().execute("INSERT INTO BALLOTS (ELECTIONID, BALLOT) VALUES (%s, %s);", (electionid, ballot))
        db.commit()
        db.close()
    
    except IntegrityError as e:
        db.close()
        
    finally:
        return {"success": True, "message": "ballot successfully casted"}
    
def get_ballots(electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()

        cursor.execute("SELECT BALLOT FROM BALLOTS WHERE ELECTIONID = %s;", (electionid,))
        rows = cursor.fetchall()

        return {"success": True, "data": rows}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
