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

ADM_URL = "http://192.168.0.112:5000"
REG_URL = "http://192.168.0.112:5001"
VAL_URL = "http://192.168.0.112:5002"
TAL_URL = "http://192.168.0.112:5003"


def createElection(end_setting, end_election, description):
    try:
        response = requests.get(f"{ADM_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([end_setting, end_election, description])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')
            
            return requests.post(f"{ADM_URL}/create_election", json={'message': enc_data_base64})
            
        else:
            return ['error', 'couldnt receive server public key.']
        
    except Exception as e:
        return ['error', e]
    
def delete_election(electionid):
    try:
        response = requests.get(f"{ADM_URL}/receive_pub_key")

        if response.status_code == 200:
            print(1)
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(electionid, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            print(1.1)
            response = requests.post(f"{ADM_URL}/delete_election", json={'message': enc_data_base64})
            print(1.2)

            if response.status_code == 200:
                print(2)
                return parse_message(response.json()['message'])
            
            else:
                print(3)
                return parse_message(response.json()['error'])
            
        else:
            print(4)
            return ['error', 'couldnt receive server public key.']
        
    except Exception as e:
        print(5)
        return ['error', e]
    
def get_elections():
    try:
        response = requests.get(f"{ADM_URL}/get_elections")

        if response.status_code == 200:
            return response.json()['elections']

        else:
            return ['erro', 'couldnt get elections']
        
    except Exception as e:
        return ['error', e]

    
def officeSetting(office_name, electionid):
    try:
        response = requests.get(f"{ADM_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([office_name, electionid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')
            
            response = requests.post(f"{ADM_URL}/office_setting", json={'message': enc_data_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
    
    except Exception as e:
        return ['error', e]
    
def applying(cpf, electionid, office_name, priv_key, pub_key):
    try:
        response = requests.get(f"{ADM_URL}/receive_pub_key")
        
        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)
            key_base64 = base64.b64encode(pub_key).decode('utf-8')

            data = pickle.dumps([cpf, electionid, office_name])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            signed_data = sign(priv_key, pub_key, data)
            enc_signed_data = encrypt_hybrid(signed_data, pub_key_s, aes_key)
            enc_signed_data_base64 = base64.b64encode(enc_signed_data).decode('utf-8')

            response = requests.post(f"{ADM_URL}/applying", json={'enc_data': enc_data_base64, 'enc_signed_data': enc_signed_data_base64, 'key': key_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
    
    except Exception as e:
        return ['error', e]
    
def registering(name, cpf, electionid):
    try:
        response = requests.get(f"{REG_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([name, cpf, electionid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{REG_URL}/registering", json={'message': enc_data_base64})

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
        response = requests.get(f"{REG_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            keys = generate()
            public_key = export_key(keys['public_key'])

            version = randint(0, 255)
            data = pickle.dumps([name, cpf, electionid, version, public_key])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{REG_URL}/authentication", json={'message': enc_data_base64})

            if response.status_code == 200:
                enc_certificate = base64.b64decode(response.json()['certificate'])
                certificate = decrypt_hybrid(enc_certificate, keys['private_key'])
                enc_key, salt = store_private_key(keys['private_key'], password)

                return ['success', certificate, enc_key, salt]
            
            else:
                print(response.json())
                return ['error', response.json()['error']]
                    
    except Exception as e:
        return ['error', e]
    
    
def get_voters():
    try:
        response = requests.get(f"{REG_URL}/get_voters")

        if response.status_code == 200:
            return response.json()['voters']
        
        else:
            return ['erro', 'couldnt get voters']
        
    except Exception as e:
        return ['error', e]
    

def search_cpf(cpf):
    print(type(cpf))
    try:
        response = requests.get(f"{REG_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(cpf, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{REG_URL}/search_cpf", json={'message': enc_data_base64})

            if response.status_code == 200:
                return True
            
            else:
                return False
            
    except Exception as e:
        return False
    
def search_name(cpf):
    try:
        response = requests.get(f"{REG_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            enc_data = encrypt_hybrid(cpf, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{REG_URL}/search_name", json={'message': enc_data_base64})

            if response.status_code == 200:
                return response.json()['message']
            
            else:
                return response.json()['message']
            
    except Exception as e:
        return response.json()['message']

    
def delete_voter(cpf, electionid):
    try:
        response = requests.get(f"{REG_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)

            data = pickle.dumps([cpf, electionid])
            enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

            response = requests.post(f"{REG_URL}/delete_voter", json={'message': enc_data_base64})

            if response.status_code == 200:
                return parse_message(response.json()['message'])
            
            else:
                return parse_message(response.json()['error'])
            
        else:
            return ['error', 'couldnt receive server public key.']
        
    except Exception as e:
        return ['error', e]

    
def get_commits(pub_key, priv_key, electionids):
    try:
        response = requests.get(f"{TAL_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_s = base64.b64decode(response.json()['key'])
            aes_key = get_random_bytes(16)
            key_base64 = base64.b64encode(pub_key).decode('utf-8')

            enc_data = base64.b64encode(encrypt_hybrid(pickle.dumps(electionids), pub_key_s, aes_key)).decode('utf-8')

            response = requests.post(f"{TAL_URL}/get_commits", json={'key': key_base64, 'data': enc_data})

            enc_commit = base64.b64decode(response.json()['commits'])
            commit = pickle.loads(decrypt_hybrid(enc_commit, priv_key))
            print(commit)

            return ["success", commit]
        
    except Exception as e:
        return ["error", e]
    
def vote(pub_key_c, priv_key_c, ballot):
    try:
        response_tal = request.get(f"{TAL_URL}/receive_pub_key")
        response_val = request.get(f"{VAL_URL}/receive_pub_key")

        if response_tal.status_code == 200 and response_val.status_code == 200:
            pub_key_t = base64.b64decode(response_tal.json()['key'])
            pub_key_v = base64.b64decode(response_val.json()['key'])
            aes_key = get_random_bytes(16)

            c_key_base64 = base64.b64encode(pub_key_c).decode('utf-8')
            t_key_base64 = base64.b64encode(pub_key_t).decode('utf-8')
            v_key_base64 = base64.b64encode(pub_key_v).decode('utf-8')

            t_enc_ballot = base64.b64encode(encrypt_hybrid(ballot, pub_key_t, aes_key)).decode('utf-8')
            c_signed_t_enc_ballot = base64.b64encode(encrypt_hybrid(sign(priv_key_c, pub_key_c, ballot), pub_key_v, aes_key))

            response = requests.post(f"{VAL_URL}/verify_ballot", json={'key': c_key_base64, 'tallier_key': t_key_base64, 'ballot': t_enc_ballot, 'signature': c_signed_t_enc_ballot})

            v_signed_t_enc_ballot = decrypt_hybrid(base64.b64decode(response.json()['signed_ballot']), priv_key_c)
            t_enc_credential = response.json()['credential']

            if verify(pub_key_v, t_enc_ballot, v_signed_t_enc_ballot):
                
                v_signed_t_enc_ballot = base64.b64encode(encrypt_hybrid(v_signed_t_enc_ballot, pub_key_t, aes_key)).decode('utf-8')
                
                response = requests.post(f"{TAL_URL}/cast_vote", json={'validator_key': v_key_base64, 
                                                                       'signed_ballot': v_signed_t_enc_ballot, 
                                                                       'ballot': t_enc_ballot, 
                                                                       'credential': t_enc_credential})
                
                return ["success", "ballot casted successfully."]

            else:
                return ['error', 'comunication error with validator server.']
            
    except Exception as e:
        return ["error", e]

def get_candidates(electionid):
    try:
        response = requests.post(f"{VAL_URL}/get_candidates", json={'electionid': electionid})
        candidates = pickle.loads(base64.b64decode(response.json()['candidates']))

        return candidates

    except Exception as e:
        return ["error", e]