from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
import socket
import datetime
import requests

SERVER_URL = "http://192.168.68.104:5000"

def parse_message(message):
    header, content = message.split(': ')
    return header, content

def electionSetting(electionid, num_offices, end_setting, end_election):
    try:
        response = requests.get(f"{SERVER_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([electionid, num_offices, end_setting, end_election])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')
            
            response = requests.post(f"{SERVER_URL}/election_setting", json={'message': enc_data_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
        
    except Exception as e:
        return ['error', e]
    
def officeSetting(office_name, electionid, digit_num):
    try:
        response = requests.get(f"{SERVER_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([office_name, electionid, digit_num])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')
            
            response = requests.post(f"{SERVER_URL}/office_setting", json={'message': enc_data_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
    
    except Exception as e:
        return ['error', e]
    
def applying(cpf, electionid, campaignid, office_name, priv_key, pub_key):
    try:
        response = requests.get(f"{SERVER_URL}/receive_pub_key")
        
        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)
            key_base64 = base64.b64encode(pub_key).decode('utf-8')

            data = pickle.dumps([cpf, electionid, office_name, campaignid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            signed_data = sign(priv_key, pub_key, data)
            enc_signed_data = encrypt_hybrid(signed_data, pub_key_s, aes_key)
            enc_signed_data_base64 = base64.b64encode(enc_signed_data).decode('utf-8')

            response = requests.post(f"{SERVER_URL}/applying", json={'enc_data': enc_data_base64, 'enc_signed_data': enc_signed_data_base64, 'key': key_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
    
    except Exception as e:
        return ['error', e]