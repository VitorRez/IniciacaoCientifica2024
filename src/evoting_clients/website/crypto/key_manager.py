from .CryptoUtils.certificate import * 
from .CryptoUtils.hash import *
from .CryptoUtils.keys import *
from .CryptoUtils.PBKDF import *
from .CryptoUtils.argon2_kdf import *
from .encrypt_hybrid import *
import base64
import datetime

def store_public_key(subject_name, subject_key, issuer_name, signed_request):

    current_time = datetime.datetime.now()

    return create_digital_certificate(current_time.minute, issuer_name, subject_name, subject_key, 'SHA256WithNTRU', 'BR', 'MG', signed_request)

def store_private_key(key, password):

    key_argon2 = argon2_kdf(password)
    enc_key = encrypt_argon2(key_argon2, key)

    return base64.b64encode(enc_key).decode('utf-8'), base64.b64encode(key_argon2['salt']).decode('utf-8') 
    
def search_public_key(certificate):

    return get_pub_key(certificate)
        
def search_private_key(password, salt, enc_key):
    enc_key = base64.b64decode(enc_key)
    salt = base64.b64decode(salt)

    key_argon2 = argon2_kdf(password, salt)
    key = decrypt_argon2(password, key_argon2, enc_key)

    return key