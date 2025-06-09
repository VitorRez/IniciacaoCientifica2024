from ..crypto.CryptoUtils.encrypt_sym import *
from ..crypto.CryptoUtils.hash import *
from ..crypto.CryptoUtils.keys import *
from ..crypto.CryptoUtils.PBKDF import *
from ..crypto.encrypt_hybrid import *
from ..crypto.key_manager import *
from ..crypto.PyNTRU.NTRU import *
from random import randint
import socket
import datetime
import requests

URL = "http://0.0.0.0:5002"

def verify_ballot(enc_ballot, password, cpf, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code != 200:
            return response.json()
        
        pub_key_s = import_key(response.json()['key'])
        aes_key = get_random_bytes(16)

        enc_electionid, ek1 = encrypt_hybrid(electionid, pub_key_s, aes_key)
        enc_cpf, ek2 = encrypt_hybrid(cpf, pub_key_s, aes_key)
        enc_password, ek3 = encrypt_hybrid(password, pub_key_s, aes_key)
        
        response = requests.post(f"{URL}/verify_ballot",
                                 json={
                                        "enc_ballot": enc_ballot,
                                        "enc_electionid": enc_electionid,
                                        "enc_cpf": enc_cpf,
                                        "enc_password": enc_password 
                                    }
                                )
        
        return response.json()
    
    except Exception as e:
        return {"success": False, "error": e}
            