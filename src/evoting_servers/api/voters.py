from .db_connector import connect_to_db, create_random_string
from .elections import search_end_setting, search_end_election
from mysql.connector import Error, IntegrityError
from datetime import datetime
import json

def create_voter(name, cpf, electionid):
    db = connect_to_db()

    current_time = datetime.now()
    end_setting = search_end_setting(electionid)["data"]
    end_election = search_end_election(electionid)["data"]

    if current_time > end_setting:
        db.close()
        return {"success": False, "error": "invalid end_setting value."}
    
    if current_time > end_election:
        db.close()
        return {"success": False, "error": "invalid end_election value."}

    try:
        db.cursor().execute("INSERT INTO VOTERS (NAME, CPF, ELECTIONID, AUTH, CANDIDATE) VALUES (%s,%s,%s,%s,%s);", (name, cpf, electionid, 0, 0))
        db.commit()
        db.close()
        return {"success": True, "message": "voter successfully created."}
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "voter already exists."}
        
        else:
            return {"success": False, "error": str(e)}


def delete_voter(cpf, electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM VOTERS WHERE CPF = %s AND ELECTIONID = %s;", (cpf, electionid))
        
        if cursor.rowcount == 0:
            db.close()
            return {"success": False, "error": "voter not found"}
        
        db.commit()
        db.close()
        return {"success": True, "message": "voter deleted succesfully!"}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    

def update_voter(cpf, name, electionid, auth, candidate, pub_key, priv_key, salt):
    db = connect_to_db()

    try:
        query = """
            UPDATE 
                VOTERS
            SET
                CPF = %s,
                NAME = %s,
                ELECTIONID = %s,
                AUTH = %s,
                CANDIDATE = %s,
                PUB_KEY = %s,
                PRIV_KEY = %s,
                SALT = %s
            WHERE
                CPF = %s AND ELECTIONID = %s;
        """ 

        db.cursor().execute(query, (cpf, name, electionid, auth, candidate, pub_key, priv_key, salt, cpf, electionid))
        db.commit()
        db.close()
        return {"success": True, "message": "voter successfuly updated."}
    
    except IntegrityError as e:
        db.close()
        return {"success": False, "error": str(e)}
    
def approve_voter(cpf, electionid):
    db = connect_to_db()
    print(cpf, electionid)

    try:
        db.cursor().execute("UPDATE VOTERS SET CANDIDATE = 2 WHERE CPF = %s AND ELECTIONID = %s;", (cpf, electionid))
        db.commit()
        db.close()
        return {"success": True, "message": "voter successfuly updated."}

    except IntegrityError as e:
        db.close()
        return {"success": False, "error": str(e)}
    

def vote(cpf, electionid):
    db = connect_to_db()

    try:
        db.cursor().execute("UPDATE VOTERS SET VOTED = 1 WHERE CPF = %s AND ELECTIONID = %s;", (cpf, electionid))
        db.commit()
        db.close()
        return {"success": True, "message": "voter successfuly updated."}

    except IntegrityError as e:
        db.close()
        return {"success": False, "error": str(e)}

    
def get_voter(cpf, electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT 
                VOTERS.CPF AS cpf,
                VOTERS.NAME AS name,
                VOTERS.ELECTIONID AS electionid,
                VOTERS.AUTH AS auth,
                VOTERS.CANDIDATE AS candidate,
                VOTERS.PUB_KEY AS pub_key,
                VOTERS.PRIV_KEY AS priv_key,
                VOTERS.SALT AS salt,
                VOTERS.VOTED AS voted,
                ELECTION.ELECTIONID as electionid,
                ELECTION.DESCRIPTION AS description,
                ELECTION.END_SETTING AS end_setting,
                ELECTION.START_ELECTION AS start_election,
                ELECTION.END_ELECTION AS end_election,
                ELECTION.START_DISCLOSURE AS start_disclosure
            FROM 
                VOTERS
            INNER JOIN
                ELECTION
            ON 
                VOTERS.ELECTIONID = ELECTION.ELECTIONID
            WHERE
                VOTERS.CPF = %s AND VOTERS.ELECTIONID = %s;
        """

        cursor.execute(query, (cpf, electionid,))
        voter = cursor.fetchone()
        cursor.close()
        db.close()

        return {"success": True, "data": voter}
    
    except Exception as e:
        db.close()
        return {"success": False, 'error': str(e)}
    
def get_voters():
    db = connect_to_db()

    try:
        cursor = db.cursor()

        query = """
            SELECT 
                VOTERS.CPF,
                VOTERS.NAME,
                VOTERS.ELECTIONID,
                VOTERS.AUTH,
                VOTERS.CANDIDATE,
                VOTERS.PUB_KEY,
                VOTERS.PRIV_KEY,
                VOTERS.SALT,
                ELECTION.ELECTIONID,
                ELECTION.DESCRIPTION,
                ELECTION.END_SETTING AS end_setting,
                ELECTION.START_ELECTION AS start_election,
                ELECTION.END_ELECTION AS end_election,
                ELECTION.START_DISCLOSURE AS start_disclosure
            FROM 
                VOTERS
            INNER JOIN
                ELECTION
            ON 
                VOTERS.ELECTIONID = ELECTION.ELECTIONID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        voters = [
            {
                "cpf": row[0],
                "name": row[1],
                "electionid": row[2],
                "auth": row[3],
                "candidate": row[4],
                "pub_key": row[5],
                "priv_key": row[6],
                "salt": row[7],
                "electionid": row[8],
                "description": row[9],
                "end_setting": row[10],
                "start_election": row[11],
                "end_election": row[12],
                "start_disclosure": row[13]
            }
            for row in rows
        ]

        return {"success": True, "data": voters}
    
    except Exception as e:
        db.close()
        return {"success": False, 'error': str(e)}
    

def get_voters_by_cpf(cpf):
    db = connect_to_db()

    try:
        cursor = db.cursor()

        query = """
            SELECT 
                VOTERS.CPF,
                VOTERS.NAME,
                VOTERS.ELECTIONID,
                VOTERS.AUTH,
                VOTERS.CANDIDATE,
                VOTERS.PUB_KEY,
                VOTERS.PRIV_KEY,
                VOTERS.SALT,
                ELECTION.ELECTIONID,
                ELECTION.DESCRIPTION,
                ELECTION.END_SETTING,
                ELECTION.START_ELECTION,
                ELECTION.END_ELECTION,
                ELECTION.START_DISCLOSURE
            FROM 
                VOTERS
            INNER JOIN
                ELECTION
            ON 
                VOTERS.ELECTIONID = ELECTION.ELECTIONID
            WHERE 
                VOTERS.CPF = %s;
        """
        
        cursor.execute(query, (cpf,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        if not rows:
            return {"success": False, "error": "Voter not found."}

        voters = [
            {
                "cpf": row[0],
                "name": row[1],
                "electionid": row[2],
                "auth": row[3],
                "candidate": row[4],
                "pub_key": row[5],
                "priv_key": row[6],
                "salt": row[7],
                "electionid": row[8],
                "description": row[9],
                "end_setting": row[10],
                "start_election": row[11],
                "end_election": row[12],
                "start_disclosure": row[13]
            }
            for row in rows
        ]

        return {"success": True, "data": voters}

    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


def get_voters_by_election(electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()

        query = """
            SELECT 
                VOTERS.CPF,
                VOTERS.NAME,
                VOTERS.ELECTIONID,
                VOTERS.AUTH,
                VOTERS.CANDIDATE,
                VOTERS.PUB_KEY,
                VOTERS.PRIV_KEY,
                VOTERS.SALT,
                ELECTION.ELECTIONID,
                ELECTION.DESCRIPTION,
                ELECTION.END_SETTING,
                ELECTION.START_ELECTION,
                ELECTION.END_ELECTION,
                ELECTION.START_DISCLOSURE
            FROM 
                VOTERS
            INNER JOIN
                ELECTION
            ON 
                VOTERS.ELECTIONID = ELECTION.ELECTIONID
            WHERE 
                VOTERS.ELECTIONID = %s;
        """
        
        cursor.execute(query, (electionid,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        if not rows:
            return {"success": False, "error": "Voter not found."}

        voters = [
            {
                "cpf": row[0],
                "name": row[1],
                "electionid": row[2],
                "auth": row[3],
                "candidate": row[4],
                "pub_key": row[5],
                "priv_key": row[6],
                "salt": row[7],
                "electionid": row[8],
                "description": row[9],
                "end_setting": row[10],
                "start_election": row[11],
                "end_election": row[12],
                "start_disclosure": row[13]
            }
            for row in rows
        ]

        return {"success": True, "data": voters}

    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}