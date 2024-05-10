from Crypto.PublicKey import RSA
from Crypto import *
from certificates.certifying_authority import *
from data_base.sql_manager import *

class registrar():

    def __init__(self):
        self.key = RSA.generate(2048)
    
    def voter_registration(self, name, cpf, id):
        reg_voter(name, cpf, id)

    def voter_authentication(self, cpf, id):
        x = search_info(cpf, id)
        print(x)
        if x:
           change_voter_status(cpf, id)