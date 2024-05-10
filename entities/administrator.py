from Crypto.PublicKey import RSA
from Crypto import *
from certificates.certifying_authority import *
from data_base.sql_manager import *

#classe que representa a entidade administrador
class administrator():

    def __init__(self):
        self.key = RSA.generate(2048)

    #metodo para um eleitor se candidatar
    def apply(self, name, cpf, id, office, campaignId):
        x = search_voter(cpf, id)
        if not x:
            return
        reg_candidate(name, cpf, id, office, campaignId)
        
        
