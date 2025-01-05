import mysql.connector
import string
import random
from mysql.connector import Error, IntegrityError
from Crypto.Random import get_random_bytes
from crypto.CryptoUtils.hash import *
from datetime import datetime
from django.utils.timezone import make_aware
from pytz import timezone

def connect_to_db():
    db = mysql.connector.connect(
        host="localhost",
        user="ELECTIONAUTH",
        password="Fr468vj#",
        database="evoting_database",
        auth_plugin='mysql_native_password'
    )
    return db


def search_num_office(electionid):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT NUM_OFFICES FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        db.close()


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
        cursor.execture("SELECT END_ELECTION FROM ELECTION WHERE ELECTIONID = %s;", (electionid,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        db.close()


def search_digit_num(electionid, name):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT DIGIT_NUM FROM OFFICES WHERE ELECTIONID = %s AND NAME = %s;", (electionid, name))
        result = cursor.fetchone()
        return result if result else None
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
        
    
def create_election(electionid, num_offices, end_setting, end_election):
    year = datetime.now().year
    db = connect_to_db()

    current_time = make_aware(datetime.now(), timezone=timezone('America/Sao_Paulo'))

    print(current_time)
    print(end_setting)

    if current_time > end_setting:
        return 'error: cant register anymore election.'

    try:
        db.cursor().execute("INSERT INTO ELECTION (ELECTIONID, YEAR, NUM_OFFICES, END_SETTING, END_ELECTION) VALUES (%s, %s, %s, %s, %s);", (electionid, year, num_offices, end_setting, end_election))
        db.commit()
        db.close()
        return 'success: election successfully created!'
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error: {e}'
        
def create_credential(electionid, credential, salt):
    db = connect_to_db()

    try:
        db.cursor().execute("INSERT INTO CREDENTIALS (CREDENTIAL, ELECTIONID, SALT) VALUES (%s, %s, %s);", (credential, electionid, salt))
        db.commit()
        db.close()
        return 'success: credential successfully created!'
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error: {e}'
        

def create_offices(name, electionid, digit_num):
    db = connect_to_db()

    end_setting = search_end_setting(electionid)

    current_time = datetime.now()

    print(current_time)
    print(end_setting)

    if current_time > end_setting:
        return 'error: cant register anymore election.'

    num_offices = search_num_office(electionid)

    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM OFFICES WHERE ELECTIONID = %s", (electionid,))
    num_registered = cursor.fetchone()[0]
    
    try:
        if num_registered < num_offices:
            db.cursor().execute("INSERT INTO OFFICES (NAME, ELECTIONID, DIGIT_NUM) VALUES (%s,%s,%s);", (name, electionid, digit_num))
            db.commit()
            db.close()
            return 'success: office successfully created!'

        else:
            db.close()
            return 'error: cant add more offices.'
        
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error: {e}'
            

def reg_voter(name, cpf, electionid):
    db = connect_to_db()

    end_setting = search_end_setting(electionid)

    current_time = datetime.now()

    print(current_time)
    print(end_setting)

    if current_time > end_setting:
        return 'error: cant register anymore election.'

    try:
        db.cursor().execute("INSERT INTO VOTERS (NAME, CPF, ELECTIONID) VALUES (%s,%s,%s);", (name, cpf, electionid))
        db.commit()
        db.close()
        return 'success: voter successfully registered!'
    
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error: {e}'
        

    
def reg_candidate(cpf, electionid, office, campaignId):
    db = connect_to_db()

    end_setting = search_end_setting(electionid)

    current_time = datetime.now()

    print(current_time)
    print(end_setting)

    if current_time > end_setting:
        return 'error: cant register anymore election.'

    digit_num = search_digit_num(electionid, office)
    try:
        if len(str(campaignId)) == digit_num[0]:
            db.cursor().execute("INSERT INTO CANDIDATES (CPF, ELECTIONID, CAMPAIGNID, OFFICE_NAME) VALUES (%s,%s,%s,%s);", (cpf, electionid, campaignId, office))
            db.commit()
            db.close()
            return 'success: candidate successfully registered!'
        
        else:
            db.close()
            return f'error: length of campaign id must be of size {digit_num[0]}'
        
    except IntegrityError as e:
        db.close()
        if e.errno == 1062:
            return 'error: duplicate entry.'
        
        else:
            return f'error: integrity error: {e}'
        
        
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

def create_commit(electionids):
    db = connect_to_db()
    current_time = datetime.now(timezone('America/Sao_Paulo'))

    try:
        cursor = db.cursor()

        format_ids = ', '.join(['%s'] * len(electionids))

        query = f"""
        SELECT
            CREDENTIALS.CREDENTIAL,
            CREDENTIALS.SALT,
            CREDENTIALS.ELECTIONID
        FROM
            CREDENTIALS
        INNER JOIN
            ELECTION
        ON 
            CREDENTIALS.ELECTIONID = ELECTION.ELECTIONID
        WHERE
            CREDENTIALS.ELECTIONID IN ({format_ids})
            AND {current_time} BETWEEN ELECTION.END_SETTING AND ELECTION.END_ELECTION;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        db.close()
        
        commits = []
        for cred, salt, electionid in rows:
            commit = create_hash((cred + salt))
            commits.append([commit, electionid])

        return commits
    
    except Exception as e:
        db.close()
        return f'error: {e}'


#testes
#1 criar eleições
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