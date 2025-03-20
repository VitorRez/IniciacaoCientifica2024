from .db_connector import connect_to_db, create_random_string
from mysql.connector import Error, IntegrityError
from datetime import datetime
import json

def create_election(end_setting, end_election, description):
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
        db.cursor().execute("INSERT INTO ELECTION (ELECTIONID, END_SETTING, END_ELECTION, DESCRIPTION) VALUES (%s, %s, %s, %s);", (electionid, end_setting, end_election, description))
        db.commit()
        db.close()
        return {"success": True, "message": "election successfully created."}
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return {"success": False, "error": "election already exists."}
        
        else:
            return {"success": False, "error": str(e)}
        

def update_election(electionid, end_setting, end_election, description):
    db = connect_to_db()

    current_time = datetime.now()

    if current_time > end_setting:
        db.close()
        return {"success": False, "error": "invalid end_setting value."}
    
    if current_time > end_election:
        db.close()
        return {"success": False, "error": "invalid end_election value."}

    try:
        db.cursor().execute("UPDATE ELECTION SET END_SETTING = %s, END_ELECTION = %s, DESCRIPTION = %s WHERE ELECTIONID = %s;", (end_setting, end_election, description, electionid))
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

        cursor.execute("SELECT ELECTIONID, END_SETTING, END_ELECTION, DESCRIPTION FROM ELECTION;")
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
                "end_election": str(row[2]),
                "description": row[3],
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