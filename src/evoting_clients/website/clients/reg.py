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

URL = "http://0.0.0.0:5001"

def create_voter(name, cpf, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([name, cpf, electionid])
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)

            response = requests.post(f"{URL}/create_voter", json={'message': enc_data})

            return response.json()
            
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def create_user(name, cpf, password):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([name, cpf, password])
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)

            response = requests.post(f"{URL}/create_user", json={'message': enc_data})

            return response.json()
            
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def authentication(name, cpf, electionid, password):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            keys = generate()
            public_key = export_key(keys['public_key'])
            enc_key, salt = store_private_key(keys['private_key'], password)

            version = randint(0, 255)
            data = pickle.dumps([name, cpf, electionid, version, public_key, enc_key, salt])
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)

            response = requests.post(f"{URL}/authentication", json={'message': enc_data})

            return response.json()
                    
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def applying(cpf, electionid, office_name):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            print(1)
            pub_key_s = import_key(response.json()['key'])
            print(2)
            aes_key = get_random_bytes(16)
            print(3)

            data = pickle.dumps([cpf, electionid, office_name])
            print(4)
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)
            print(5)

            response = requests.post(f"{URL}/applying", json={'message': enc_data})
            print(6)

            return response.json()
        
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}


def get_voters():
    try:
        response = requests.get(f"{URL}/get_voters")

        return response.json()
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def get_users():
    try:
        response = requests.get(f"{URL}/get_users")

        return response.json()
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def get_user(cpf):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data, ephemeral_key = encrypt_hybrid(cpf, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_user", json={'message': enc_data})

            return response.json()
        
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}

            
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def is_staff(cpf):
    user = get_user(cpf)['data']

    if user['is_staff'] == 1:
        return True
    else:
        return False
    
def get_voters_by_cpf(cpf):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data, ephemeral_key = encrypt_hybrid(cpf, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_voters_by_cpf", json={'message': enc_data})

            return response.json()

        else:
            return {"success": False, "error": "coundn't access the registrator public key."}
           
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}

    
def get_voters_by_election(electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")
        
        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data, ephemeral_key = encrypt_hybrid(electionid, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_voters_by_election", json={'message': enc_data})

            return response.json()

        else:
            return {"success": False, "error": "coundn't access the registrator public key."}
           
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def get_voter(cpf, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([cpf, electionid])
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_voter", json={'message': enc_data})

            return response.json()
            
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}

    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}
    
def approve_voter(cpf, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([cpf, electionid])
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)
            
            response = requests.post(f"{URL}/approve_voter", json={'message': enc_data})
            return response.json()

        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}

def delete_voter(cpf, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([cpf, electionid])
            enc_data, ephemeral_key = encrypt_hybrid(data, pub_key_s, aes_key)

            response = requests.post(f"{URL}/delete_voter", json={'message': enc_data})

            return response.json()
            
        else:
            return {"success": False, "error": "coundn't access the registrator public key."}

    except Exception as e:
        return {"success": False, "error": f"error on registrator client: {e}"}