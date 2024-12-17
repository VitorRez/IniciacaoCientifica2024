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

SERVER_URL = "http://192.168.0.107:5001"

def parse_message(message):
    header, content = message.split(': ')
    return header, content

def registering(name, cpf, electionid):
    try:
        response = requests.get(f"{SERVER_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([name, cpf, electionid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{SERVER_URL}/registering", json={'message': enc_data_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
                    
    except Exception as e:
        return ['error', e]
    
def authentication(name, cpf, electionid, password):
    try:
        response = requests.get(f"{SERVER_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            keys = generate()
            public_key = export_key(keys['public_key'])

            version = randint(0, 255)
            data = pickle.dumps([name, cpf, electionid, version, public_key])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{SERVER_URL}/authentication", json={'message': enc_data_base64})

            enc_certificate = base64.b64decode(response.json()['certificate'])
            certificate = decrypt_hybrid(enc_certificate, keys['private_key'])
            enc_key, salt = store_private_key(keys['private_key'], password)
            return certificate, enc_key, salt 
                    
    except Exception as e:
        return ['error', e]