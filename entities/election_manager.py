from data_base.sql_manager import create_election, create_offices
from Crypto.PublicKey import RSA

class election_manager():

    def __init__(self):
        self.key = RSA.generate(2048)

    def create_election(self, id, num_offices):
        create_election(id, num_offices)

    def create_offices(self, name, id, digit_num):
        create_offices(name, id, digit_num)