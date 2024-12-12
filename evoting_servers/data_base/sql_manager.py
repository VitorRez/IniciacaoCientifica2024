import mysql.connector
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

def search_num_office(id):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT NUM_OFFICES FROM ELECTION WHERE ELECTIONID = %s;", id)
    return cursor.rowcount

def create_election(id, num_offices):
    year = datetime.now().year
    db = connect_to_db()
    db.cursor().execute("INSERT INTO ELECTION (ELECTIONID, YEAR, NUM_OFFICES) VALUES (%s, %s, %s);", (id, year, num_offices))
    db.commit()

def create_offices(name, id, digit_num):
    db = connect_to_db()
    db.cursor().execute("INSERT INTO OFFICES (NAME, ELECTIONID, DIGIT_NUM) VALUES (%s,%s,%s);", (name, id, digit_num))
    db.commit()

def reg_voter(name, cpf, id):
    db = connect_to_db()
    db.cursor().execute("INSERT INTO VOTERS (NAME, CPF, ELECTIONID) VALUES (%s,%s,%s);", (name, cpf, id))
    db.commit()

def search_voter(cpf, id):
    db = connect_to_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT * FROM VOTERS WHERE CPF = %s AND ELECTIONID = %s;", (cpf, id))
    if cursor.rowcount > 0:
        return True
    else:
        return False
    
def reg_candidate(cpf, electionid, office, campaignId):
    db = connect_to_db()
    db.cursor().execute("INSERT INTO CANDIDATES (CPF, ELECTIONID, CAMPAIGNID, OFFICE_NAME) VALUES (%s,%s,%s,%s);", (cpf, electionid, campaignId, office))
    db.commit()

#testes
#1 criar eleições
#create_election(1,2)
#create_election(2)
#create_election(3)

#2 criar cargos
#create_offices('presidente', 1, 10)
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
#print(c)