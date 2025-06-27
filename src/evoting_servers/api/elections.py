from .db_connector import connect_to_db, create_random_string
from mysql.connector import Error, IntegrityError
from datetime import datetime
import json

def create_election(end_setting, start_election, end_election, start_disclosure, description):
    db = connect_to_db()

    current_time = datetime.now()
    electionid = create_random_string(15)

    if current_time > end_setting:
        db.close()
        return {"success": False, "error": "invalid end_setting value."}
    
    if current_time > end_election:
        db.close()
        return {"success": False, "error": "invalid end_election value."}

    try:
        db.cursor().execute("INSERT INTO ELECTION (ELECTIONID, END_SETTING, START_ELECTION, END_ELECTION, START_DISCLOSURE, DESCRIPTION) VALUES (%s, %s, %s, %s, %s, %s);", (electionid, end_setting, start_election, end_election, start_disclosure, description))
        db.commit()
        db.close()
        return {"success": True, "message": "election successfully created."}
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "election already exists."}
        
        else:
            return {"success": False, "error": str(e)}
        

def update_election(electionid, end_setting, start_election, end_election, start_disclosure, description):
    db = connect_to_db()
    
    if end_setting > end_election:
        db.close()
        return {"success": False, "error": "invalid end_election value."}

    try:
        db.cursor().execute("UPDATE ELECTION SET END_SETTING = %s, START_ELECTION = %s, END_ELECTION = %s, START_DISCLOSURE = %s, DESCRIPTION = %s WHERE ELECTIONID = %s;", (end_setting, start_election, end_election, start_disclosure, description, electionid))
        db.commit()
        db.close()
        return {"success": True, "message": "election successfully updated."}
    
    except IntegrityError as e:
        db.close()
        return {"success": False, "error": str(e)}

        
def delete_election(electionid):
    db = connect_to_db()
    
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        
        if cursor.rowcount == 0:
            db.close()
            return {"success": False, "error": "election not found."}

        db.commit()
        db.close()
        return {"success": True, "message": "election successfully deleted!"}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    
def get_elections():
    db = connect_to_db()

    try:
        cursor = db.cursor()

        cursor.execute("SELECT ELECTIONID, END_SETTING, START_ELECTION, END_ELECTION, START_DISCLOSURE, DESCRIPTION FROM ELECTION;")
        elections_data = cursor.fetchall()

        elections = []
        for row in elections_data:
            electionid = row[0]

            cursor.execute("SELECT COUNT(*) FROM VOTERS WHERE ELECTIONID = %s;", (electionid,))
            num_voters = cursor.fetchone()[0]

            cursor.execute("SELECT NAME FROM OFFICES WHERE ELECTIONID = %s;", (electionid,))
            offices = [office[0] for office in cursor.fetchall()]

            elections.append({
                "electionid": electionid,
                "end_setting": str(row[1]),
                "start_election": str(row[2]),
                "end_election": str(row[3]),
                "start_disclosure": str(row[4]),
                "description": row[5],
                "num_voters": num_voters,
                "num_offices": len(offices),
                "offices": offices
            })

        cursor.close()
        db.close()

        return {"success": True, "data": elections}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}


    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    
def get_election(electionid):
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT ELECTIONID, END_SETTING, START_ELECTION, END_ELECTION, START_DISCLOSURE, DESCRIPTION FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        election = cursor.fetchone()
        
        if not election:
            db.close()
            return {"success": False, "error": "Election not found."}
        
        cursor.execute("SELECT * FROM OFFICES WHERE ELECTIONID = %s;", (electionid,))
        offices = cursor.fetchall()


        cursor.execute("SELECT COUNT(*) FROM VOTERS WHERE ELECTIONID = %s;", (electionid,))
        num_voters = cursor.fetchone()['COUNT(*)']

        
        election = {
            "electionid": election['ELECTIONID'],
            "end_setting": election['END_SETTING'],
            "start_election": election['START_ELECTION'],
            "end_election": election['END_ELECTION'],
            "start_disclosure": election['START_DISCLOSURE'],
            "description": election['DESCRIPTION'],
            "num_voters": num_voters,
            "num_offices": len(offices),
            "offices": []
        }
        
        for office in offices:
            office_name = office["NAME"]

            query = """
                SELECT
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
                    VOTERS.ELECTIONID = %s AND CANDIDATES.ELECTIONID = %s AND CANDIDATES.OFFICE_NAME = %s;
            """

            cursor.execute(query, (electionid, electionid, office_name))
            candidates = cursor.fetchall()
            
            election["offices"].append({
                "office_name": office_name,
                "candidates": candidates
            })
        
        db.close()
        return {"success": True, "data": election}
    
    except Exception as e:
        db.close()
        return {"success": False, "error": str(e)}
    
    
def search_end_setting(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT END_SETTING FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()

        if result:
            db.close()
            return {"success": True, "data": result[0]}
        
        else:
            db.close()
            return {"success": False, "error": "couldn't find this election."}
        
    finally:
        cursor.close()
        db.close()


def search_start_election(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT START_ELECTION FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()

        if result:
            db.close()
            return {"success": True, "data": result[0]}
        
        else:
            db.close()
            return {"success": False, "error": "couldn't find this election."}
        
    finally:
        cursor.close()
        db.close()


def search_end_election(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT END_ELECTION FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()
        
        if result:
            db.close()
            return {"success": True, "data": result[0]}
        
        else:
            db.close()
            return {"success": False, "error": "couldn't find this election."}
        
    finally:
        cursor.close()
        db.close()


def search_start_disclosure(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT START_DISCLOSURE FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()

        if result:
            db.close()
            return {"success": True, "data": result[0]}
        
        else:
            db.close()
            return {"success": False, "error": "couldn't find this election."}
        
    finally:
        cursor.close()
        db.close()
