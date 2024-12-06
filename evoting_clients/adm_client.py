from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
import socket
import datetime

HEADER = 16384
PORT = 5051
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

def electionSetting(electionid, num_offices):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    aes_key = get_random_bytes(16)

    pub_key_s = client.recv(HEADER)

    text = 'election_setting'
    enc_text = encrypt_hybrid(text, pub_key_s, aes_key)
    send(enc_text, client)

    data = pickle.dumps([electionid, num_offices])
    enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
    send(enc_data, client)

    print(client.recv(HEADER).decode('utf-8'))

def officeSetting(office_name, electionid, digit_num):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    aes_key = get_random_bytes(16)

    pub_key_s = client.recv(HEADER)

    text = 'office_setting'
    enc_text = encrypt_hybrid(text, pub_key_s, aes_key)
    send(enc_text, client)

    data = pickle.dumps([office_name, electionid, digit_num])
    enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
    send(enc_data, client)

    print(client.recv(HEADER).decode('utf-8'))

def applying(cpf, electionid, campaignid, office_name, priv_key, pub_key):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    aes_key = get_random_bytes(16)

    pub_key_s = client.recv(HEADER)

    text = 'applying'
    enc_text = encrypt_hybrid(text, pub_key_s, aes_key)
    send(enc_text, client)

    send(pub_key, client)

    data = pickle.dumps([cpf, electionid, office_name, campaignid])
    enc_data = encrypt_hybrid(data, pub_key_s, aes_key)
    signed_data = sign(priv_key, pub_key, data)
    enc_signed_data = encrypt_hybrid(signed_data, pub_key_s, aes_key)

    send(enc_signed_data, client)
    send(enc_data, client)
    
    print(client.recv(HEADER).decode('utf-8'))

