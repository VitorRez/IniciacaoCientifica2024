from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from random import randint
import socket
import datetime
import requests

SERVER_URL = "http://192.168.68.104:5003"

def parse_message(message):
    header, content = message.split(': ')
    return header, content

def get_commits(pub_key, priv_key, electionids):
    try:
        response = requests.get(f"{SERVER_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)
            key_base64 = base64.b64encode(pub_key).decode('utf-8')

            enc_data = base64.b64encode(encrypt_hybrid(pickle.dumps(electionids), pub_key_s, aes_key)).decode('utf-8')

            response = requests.post(f"{SERVER_URL}/get_commits", json={'key': key_base64, 'data': enc_data})

            enc_commit = base64.b64decode(response.json()['commits'])
            commit = pickle.loads(decrypt_hybrid(enc_commit, priv_key))

            return ["success", commit]
        
    except Exception as e:
        return ["error", e]