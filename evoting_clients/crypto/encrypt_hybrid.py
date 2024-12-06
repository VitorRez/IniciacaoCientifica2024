from .CryptoUtils.encrypt_sym import *
from .PyNTRU.NTRU import *
import pickle

def encrypt_hybrid(msg, pub_key, aes_key):
    nonce, ciphertext = encrypt_sym(aes_key, msg)
    enc_key = encrypt(pub_key, aes_key)

    return pickle.dumps([nonce, ciphertext, enc_key])

def decrypt_hybrid(enc_msg, priv_key):
    nonce, ciphertext, enc_key = pickle.loads(enc_msg)
    aes_key = decrypt(priv_key, enc_key)
    
    return decrypt_sym(aes_key, nonce, ciphertext)
