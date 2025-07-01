from .db_connector import connect_to_db, create_random_string
from .elections import search_end_setting, search_end_election
from mysql.connector import Error, IntegrityError
from datetime import datetime
import json

def create_candidate(cpf, electionid, office):
    db = connect_to_db()

    current_time = datetime.now()
    end_setting = search_end_setting(electionid)["data"]

    if current_time > end_setting:
        db.close()
        return {"success": False, "error": "invalid end_setting value."}
    
    try:
        print(office)
        db.cursor().execute("INSERT INTO CANDIDATES (CPF, ELECTIONID, OFFICE_NAME, APPROVED) VALUES (%s,%s,%s,%s);", (cpf, electionid, office, 0))
        db.commit()
        db.close()
        return {"success": True, "message": "candidate successfully created!"}
        
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "candidate already exists."}
        
        else:
            return {"success": False, "error": str(e)}
        
        
def approve_candidate(cpf, electionid, office):
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
        db.cursor().execute("UPDATE CANDIDATES SET APPROVED = 1 WHERE CPF = %s AND ELECTIONID = %s AND TRIM(OFFICE_NAME) = TRIM(%s);", (cpf, electionid, office))
        db.commit()
        db.close()
        return {"success": True, "message": "candidate successfully approved!"}
    
    except IntegrityError as e:
        db.close()
        return {"success": False, "error": str(e)}
    
        
def get_candidates(electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT
                VOTERS.ELECTIONID AS electionid,
                CANDIDATES.OFFICE_NAME AS office_name,
                VOTERS.NAME AS name,
                VOTERS.CPF AS cpf,
                CANDIDATES.APPROVED AS approved
            FROM
                VOTERS
            INNER JOIN
                CANDIDATES
            ON 
                VOTERS.CPF = CANDIDATES.CPF
            WHERE
                VOTERS.ELECTIONID = %s AND CANDIDATES.ELECTIONID = %s;
        """

        cursor.execute(query, (electionid, electionid))
        results = cursor.fetchall()
        db.close

        return {"success": True, "data": results}

    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}