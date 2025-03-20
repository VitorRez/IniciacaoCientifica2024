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

URL = "http://0.0.0.0:5000"

def create_election(end_setting, end_election, description):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([end_setting, end_election, description])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            
            response = requests.post(f"{URL}/create_election", json={'message': enc_data})
            
            return response.json()

        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    
def update_election(electionid, end_setting, end_election, description):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([electionid, end_setting, end_election, description])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            
            response = requests.post(f"{URL}/update_election", json={'message': enc_data})
            return response.json()

        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    
def delete_election(electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(electionid, pub_key_s, aes_key)

            response = requests.post(f"{URL}/delete_election", json={'message': enc_data})

            return response.json()
            
        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    
def get_elections():
    try:
        response = requests.get(f"{URL}/get_elections")

        return response.json()
        
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    
def get_offices():
    try:
        response = requests.get(f"{URL}/get_offices")
        
        return response.json()
    
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    

def create_office(office_name, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([office_name, electionid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            
            response = requests.post(f"{URL}/create_office", json={'message': enc_data})

            return response.json()
            
        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    

def delete_office(office_name, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([office_name, electionid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            
            response = requests.post(f"{URL}/delete_office", json={'message': enc_data})

            return response.json()
        
        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
        
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}

    

def get_candidates(electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")
        
        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(electionid, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_candidates", json={'message': enc_data})

            return response.json()

        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
           
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}
    

def get_offices_by_election(electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")
        
        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(electionid, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_offices_by_election", json={'message': enc_data})
            
            return response.json()

        else:
            return {"success": False, "error": "coundn't access the administrator public key."}
           
    except Exception as e:
        return {"success": False, "error": f"error on administrator client: {e}"}