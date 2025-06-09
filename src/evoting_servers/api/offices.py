from .db_connector import connect_to_db, create_random_string
from .elections import search_end_setting, search_end_election
from mysql.connector import Error, IntegrityError
from datetime import datetime
import json

def create_office(name, electionid):
    db = connect_to_db()

    current_time = datetime.now()
    end_setting = search_end_setting(electionid)['data']
    end_election = search_end_election(electionid)['data']

    if current_time > end_setting:
        db.close()
        return {"success": False, "error": "invalid end_setting value."}
    
    if current_time > end_election:
        db.close()
        return {"success": False, "error": "invalid end_election value."}
    
    try:
        db.cursor().execute("INSERT INTO OFFICES (NAME, ELECTIONID) VALUES (%s,%s);", (name, electionid))
        db.commit()
        db.close()
        return {"success": True, "message": "office successfully created!"}
        
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "office already exists."}
        
        else:
            return {"success": False, "error": str(e)}
        
def delete_office(name, electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM OFFICES WHERE NAME = %s AND ELECTIONID = %s;", (name, electionid,))
        
        if cursor.rowcount == 0:
            db.close()
            return {"success": False, "error": "office not found."}

        db.commit()
        db.close()
        return {"success": True, "message": "office successfully deleted!"}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    
def get_offices():
    db = connect_to_db()

    try:
        cursor = db.cursor()

        query = """
            SELECT 
                OFFICES.NAME,
                OFFICES.ELECTIONID,
                ELECTION.DESCRIPTION
            FROM
                OFFICES
            INNER JOIN
                ELECTION
            ON 
                OFFICES.ELECTIONID = ELECTION.ELECTIONID;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        offices = [{
                "office_name": row[0],
                "electionid": row[1],
                "description": row[2]
            }
            for row in rows
        ]

        return {"success": True, "data": offices}
    
    except Exception as e:
        db.close()
        return {"success": False, 'error': str(e)}
    
def get_offices_by_election(electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT NAME FROM OFFICES WHERE ELECTIONID = %s;", (electionid, ))
        
        results = cursor.fetchall()

        if results:
            return {"success": True, "data": results}
        else:
            return {"success": False, "error": "offices not found."}
        
    finally:
        cursor.close()
        db.close()