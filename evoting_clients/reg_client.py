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

HEADER = 16384
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

def send(message, client):
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def registering(name, cpf, electionid):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    aes_key = get_random_bytes(16)
    pub_key_s = client.recv(HEADER)

    text = 'registering'
    enc_text = encrypt_hybrid(text, pub_key_s, aes_key)
    send(enc_text, client)

    data = pickle.dumps([name, cpf, electionid])
    enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
    send(enc_data, client)

    print(client.recv(HEADER).decode('utf-8'))

def authentication(name, cpf, electionid, password):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    aes_key = get_random_bytes(16)
    pub_key_s = client.recv(HEADER)

    text = 'authentication'
    enc_text = encrypt_hybrid(text, pub_key_s, aes_key)
    send(enc_text, client)

    keys = generate()
    public_key = export_key(keys['public_key'])

    version = randint(0, 255)
    data = pickle.dumps([name, cpf, electionid, version, public_key])
    enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
    send(enc_data, client)

    enc_cert = client.recv(HEADER)

    if enc_cert != b'ERROR':
        certificate = decrypt_hybrid(enc_cert, keys['private_key'])

        enc_key, salt = store_private_key(keys['private_key'], password)

        return certificate, enc_key, salt 

    else:
        print('There was an error while authenticating this voter.')
