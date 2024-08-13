from Crypto.PublicKey import RSA
from .crypto.ciphers import *
from .crypto.PBKDF import *
from .crypto.hash import *

def store_private_key(salt, key, password):

    nonce, enc_key = encrypt_pbkdf(key, password, salt)
    p_hash = create_hash(password)
    return nonce, enc_key, p_hash
    
def search_public_key(certificate):

    text = certificate.split("pub:\n            ")
    text = text[1].split("Signature")
    pubkey = RSA.import_key(text[0])
    return pubkey
        
def search_private_key(password, salt, nonce, p_hash, enc_key):

    x = verify_hash(password, p_hash)
    if x:
        key = decrypt_pbkdf(nonce, enc_key, password, salt)
        return key
    else:
        return None

def store_salt(id, salt):

    filename = f"{id}_salt.txt"
    with open(filename, "wb") as file:
        file.write(salt)

def get_salt(id):

    filename = f"{id}_salt.txt"
    with open(filename, "rb") as file:
        salt = file.read()
        return salt
    
def store_hash(id, hash):

    filename = f"{id}_hash.txt"
    with open(filename, "wb") as file:
        file.write(hash)

def get_hash(id):

    filename = f"{id}_hash.txt"
    with open(filename, "rb") as file:
        hash = file.read()
        return hash