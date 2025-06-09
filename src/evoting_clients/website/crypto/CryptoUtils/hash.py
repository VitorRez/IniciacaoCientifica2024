from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import base64
import pickle

def create_hash(text, salt=None):
    if salt == None:
        salt = get_random_bytes(64)
    if isinstance(text, str):
        text = text.encode('utf-8')
    thash = SHA256.new(text+salt)

    return base64.b64encode(pickle.dumps([thash.digest(), salt])).decode('utf-8')

def verify_hash(text, t_hash):
    t_hash = base64.b64decode(t_hash)
    
    t_hash, salt = pickle.loads(t_hash)
    if isinstance(text, str):
        text = text.encode('utf-8')
    t_hash1 = SHA256.new(text+salt)
    return t_hash == t_hash1.digest()

def get_salt(t_hash):
    t_hash = base64.b64decode(t_hash)
    t_hash, salt = pickle.loads(t_hash)

    return(salt)

def verify_hash_with_hash(t_hash1, t_hash2):
    if isinstance(t_hash1, bytes):
        t_hash1 = t_hash1.decode()

    if isinstance(t_hash2, bytes):
        t_hash2 = t_hash2.decode()

    return t_hash1 == t_hash2
