import mysql.connector
import string
import random
import json
from mysql.connector import Error, IntegrityError
from Crypto.Random import get_random_bytes
from crypto.CryptoUtils.hash import *
from datetime import datetime


def connect_to_db():
    db = mysql.connector.connect(
        host="localhost",
        user="ELECTIONAUTH",
        password="Fr468vj#",
        database="evoting_database",
        auth_plugin='mysql_native_password'
    )
    return db


def create_random_string(size):
    s = string.ascii_uppercase + string.digits
    return ''.join(random.choices(s, k=size))



def search_end_setting(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT END_SETTING FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        db.close()


def search_end_election(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT END_ELECTION FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        db.close()


def search_voter(cpf, electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT * FROM VOTERS WHERE CPF = %s AND ELECTIONID = %s;", (cpf, electionid))
        if cursor.rowcount > 0:
            return True
        else:
            return False
    finally:
        cursor.close()
        db.close()


def search_cpf(cpf):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT *  FROM VOTERS WHERE CPF = %s;", (cpf,))
        if cursor.rowcount > 0:
            return True
        else:
            return False
    finally:
        cursor.close()
        db.close()

    
def search_name(cpf):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT NAME FROM VOTERS WHERE CPF = %s;", (cpf,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        db.close()
        
    
def create_election(end_setting, end_election, description):
    db = connect_to_db()

    current_time = datetime.now()
    electionid = create_random_string(15)

    if current_time > end_setting:
        db.close()
        return 'error: cant register this election.'

    try:
        db.cursor().execute("INSERT INTO ELECTION (ELECTIONID, END_SETTING, END_ELECTION, DESCRIPTION) VALUES (%s, %s, %s, %s);", (electionid, end_setting, end_election, description))
        db.commit()
        db.close()
        return 'success: election successfully created!'
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error {e}'
        

def delete_election(electionid):
    db = connect_to_db()
    
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        
        if cursor.rowcount == 0:
            db.close()
            return 'error: election not found.'

        db.commit()
        db.close()
        return 'success: election successfully deleted!'
    
    except Exception as e:
        db.close()
        return f'error: {e}'

        
def create_credential(electionid):
    db = connect_to_db()

    try:
        credential = create_random_string(256).encode()
        salt = get_random_bytes(16)

        db.cursor().execute("INSERT INTO CREDENTIALS (CREDENTIAL, ELECTIONID, SALT) VALUES (%s, %s, %s);", (credential, electionid, salt))
        db.commit()
        db.close()
        return 'success: credential successfully created!'
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error {e}'
        

def create_offices(name, electionid):
    db = connect_to_db()

    end_setting = search_end_setting(electionid)

    current_time = datetime.now()

    print(current_time)
    print(end_setting)

    if current_time > end_setting:
        return 'error: cant register anymore election.'
    
    try:
        db.cursor().execute("INSERT INTO OFFICES (NAME, ELECTIONID) VALUES (%s,%s);", (name, electionid))
        db.commit()
        db.close()
        return 'success: office successfully created!'
        
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error {e}'
            

def reg_voter(name, cpf, electionid):
    db = connect_to_db()

    end_setting = search_end_setting(electionid)

    current_time = datetime.now()

    print(name, cpf, electionid)

    if current_time > end_setting:
        print(1)
        return 'error: cant register anymore election.'

    try:
        db.cursor().execute("INSERT INTO VOTERS (NAME, CPF, ELECTIONID) VALUES (%s,%s,%s);", (name, cpf, electionid))
        db.commit()
        db.close()
        print(2)
        return 'success: voter successfully registered!'
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            print(3)
            return 'error: duplicate entry.'
        
        else:
            print(4)
            print(e)
            return f'error: integrity error {e}'
        

def get_voters():
    db = connect_to_db()

    try:
        cursor = db.cursor()

        query = """
            SELECT 
                VOTERS.CPF,
                VOTERS.NAME,
                VOTERS.ELECTIONID,
                ELECTION.DESCRIPTION
            FROM
                VOTERS
            INNER JOIN
                ELECTION
            ON 
                VOTERS.ELECTIONID = ELECTION.ELECTIONID;
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
                "description": row[3]
            }
            for row in rows
        ]

        return voters
    
    except Exception as e:
        db.close()
        return json.dumps({'error': str(e)})
            

def delete_voter(cpf, electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM VOTERS WHERE CPF = %s AND ELECTIONID = %s;", (cpf, electionid))
        
        if cursor.rowcount == 0:
            db.close()
            return 'error: voter not found'
        
        db.commit()
        db.close()
        return 'success: voter successfully deleted!'
    
    except Exception as e:
        db.close()
        return f'error: {e}'

    
def reg_candidate(cpf, electionid, office):
    db = connect_to_db()

    end_setting = search_end_setting(electionid)

    current_time = datetime.now()

    print(current_time)
    print(end_setting)

    if current_time > end_setting:
        return 'error: cant register anymore election.'
    
    try:
        db.cursor().execute("INSERT INTO CANDIDATES (CPF, ELECTIONID, CAMPAIGNID, OFFICE_NAME) VALUES (%s,%s,%s);", (cpf, electionid, office))
        db.commit()
        db.close()
        return 'success: candidate successfully registered!'
        
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error {e}'
        
        
def delete_voter(cpf, electionid):
    db = connect_to_db()

    try:
        cursor = db.cursor()
        rows_affected = cursor.execute("DELETE FROM VOTERS WHERE CPF = %s AND ELECTIONID = %s;", (cpf, electionid))
        db.commit()
        db.close()

        if rows_affected > 0:
            return 'success: voter successfully deleted!'
        else:
            return 'error: voter not found for the specified CPF and Election ID.'

    except Exception as e:
        db.close()
        return f'error: {e}'

def create_commit(electionid):
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

        return commits
    
    except Exception as e:
        db.close()
        return f'error: {e}'
    
    
def get_elections():
    db = connect_to_db()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT ELECTIONID, END_SETTING, END_ELECTION, DESCRIPTION FROM ELECTION;")
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        elections = [
            {
                "electionid": row[0],
                "end_setting": str(row[1]),
                "end_election": str(row[2]),
                "description": row[3]
            }
            for row in rows
        ]

        return elections

    except Exception as e:
        db.close()
        return json.dumps({'error': str(e)})

    
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

        return results

    except Exception as e:
        db.close()
        return f'error: {e}'

#testes
#1 criar eleições"
#create_election(1,2)
#create_election(2)
#create_election(3)

#2 criar cargos
#create_offices('presidente', 1, 2)
#create_offices('presidente', 2, 1)
#create_offices('vice presidente', 2, 2)
#create_offices('presidente', 3, 2)
#create_offices('vice presidente', 3, 3)
#create_offices('secretario', 3, 4)

#4 adicionar eleitores
#reg_voter('vitor', '12373075628', 1)
#reg_voter('lucia', '11111111111', 1)

#5 autenticar eleitor
#change_voter_status('12373075628', 1)

#6 lançar candidatura
#reg_candidate('12373075628', '1', 'presidente', '13')

#7 buscar eleitor
#x = search_voter(12373075628, 1)
#y = search_voter(11111111111, 1)
#print(x, y)

#8 buscar dados
#a = search_info(12373075628, 1)
#b = search_info(11111111111, 1)
#print(a, b)

#9 busca numero de cargos por eleição
#c = search_num_office(int(1))