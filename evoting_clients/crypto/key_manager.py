from .CryptoUtils.certificate import * 
from .CryptoUtils.hash import *
from .CryptoUtils.keys import *
from .CryptoUtils.PBKDF import *
from .encrypt_hybrid import *
import datetime

def store_public_key(subject_name, subject_key, issuer_name, signed_request):

    current_time = datetime.datetime.now()

    return create_digital_certificate(current_time.minute, issuer_name, subject_name, subject_key, 'SHA256WithNTRU', 'BR', 'MG', signed_request)

def store_private_key(key, password):

    key_pbkdf = PBKDF(password)
    enc_key = encrypt_pbkdf(key_pbkdf, key)

    return enc_key, key_pbkdf['salt']
    
def search_public_key(certificate):

    return get_pub_key(certificate)
        
def search_private_key(password, salt, enc_key):

    pbkdf_key = PBKDF(password, salt)
    key = decrypt_pbkdf(password, pbkdf_key, enc_key)

    return key