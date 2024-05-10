from Crypto.PublicKey import RSA
from Crypto import *
from certificates.certifying_authority import *
from data_base.sql_manager import *

class autorithy():

    def __init__(self):
        self.key = RSA.generate(2048)