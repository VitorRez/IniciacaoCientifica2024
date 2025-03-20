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

URL = "http://0.0.0.0:5003"

def get_commits(electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(electionid, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_commits", json={'data': enc_data})

            return response.json()
        
    except Exception as e:
        return ["error", e]