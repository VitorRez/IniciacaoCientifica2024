from .CryptoUtils.encrypt_sym import *
from .PyNTRU.NTRU import *
import base64
import pickle

def encrypt_hybrid(msg, pub_key, aes_key):
    nonce, ciphertext = encrypt_sym(aes_key, msg)
    enc_key, ephemeral_key = encrypt(pub_key, aes_key)

    enc_msg = pickle.dumps([nonce, ciphertext, enc_key, ephemeral_key])

    return base64.b64encode(enc_msg).decode('utf-8'), ephemeral_key

def decrypt_hybrid(enc_msg, priv_key):
    enc_msg = base64.b64decode(enc_msg)

    nonce, ciphertext, enc_key, ephemeral_key = pickle.loads(enc_msg)
    aes_key = decrypt(priv_key, enc_key)
    
    return decrypt_sym(aes_key, nonce, ciphertext)
