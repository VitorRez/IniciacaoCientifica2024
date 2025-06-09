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

            enc_data, ephemeral_key = encrypt_hybrid(electionid, pub_key_s, aes_key)

            response = requests.post(f"{URL}/get_commits", json={'message': enc_data})

            return response.json()
        
    except Exception as e:
        return {"success": False, "error": e}
    
def prepare_ballot(ballot):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = import_key(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_ballot, ephemeral_key = encrypt_hybrid(ballot, pub_key_s, aes_key)

            return {"success": True, "enc_ballot": enc_ballot, "ephemeral_key": ephemeral_key, 'pub_key': response.json()['key']}
    
    except Exception as e:
        return {"success": False, "error": e}
    
def cast_ballot(signed_ballot, enc_ballot, enc_credential, electionid):
    try:
        response = requests.get(f"{URL}/receive_pub_key")

        if response.status_code != 200:
            return response.json()
        
        pub_key_s = import_key(response.json()['key'])
        aes_key = get_random_bytes(16)
        
        enc_electionid, ephemeral_key = encrypt_hybrid(electionid, pub_key_s, aes_key)
        
        response = requests.post(f"{URL}/cast_ballot", json={"signed_ballot": signed_ballot, "enc_ballot": enc_ballot, "enc_credential": enc_credential, "enc_electionid": enc_electionid})

        return response.json()
    
    except Exception as e:
        return {"success": False, "error": e}