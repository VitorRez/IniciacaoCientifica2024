from argon2.low_level import hash_secret_raw, Type
from Crypto.Random import get_random_bytes
from .encrypt_sym import *
from .hash import *
import base64
import pickle

# Password-Based Key Derivation Function using Argon2
def argon2_kdf(password, salt=None):
    if salt is None:
        salt = get_random_bytes(16)

    key = hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=3,      
        memory_cost=2**16, 
        parallelism=1,    
        hash_len=16,      
        type=Type.ID     
    )

    p_hash = create_hash(password)

    return {'key': key, 'salt': salt, 'p_hash': p_hash}

def encrypt_argon2(key_argon2, key_ntru):
    return pickle.dumps(encrypt_sym(key_argon2['key'], pickle.dumps(key_ntru)))

def decrypt_argon2(password, key_argon2, enc_key):
    nonce, ciphertext = pickle.loads(enc_key)

    derived_key_data = argon2_kdf(password, key_argon2['salt'])

    if derived_key_data['p_hash'] != key_argon2['p_hash']:
        dummy_key_ntru = get_random_bytes(16)
        return dummy_key_ntru

    key_ntru = decrypt_sym(derived_key_data['key'], nonce, ciphertext)
    return pickle.loads(key_ntru)
