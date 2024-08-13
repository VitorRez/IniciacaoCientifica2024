import socket
from .crypto.ciphers import *
from .crypto.PBKDF import *
from .key_manager import *
from .certificates.certifying_authority import *
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

HEADER = 2048
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


def send(msg, client):
    message = msg
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def registration(msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    rsa_key = RSA.import_key(client.recv(2048))
    aes_key = get_random_bytes(16)
    e = CipherHandler(rsa_key, aes_key)
    enc_text = e.e_protocol(msg)
    send(enc_text, client)
    client.close()

def authentication(msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    rsa_key = RSA.import_key(client.recv(2048))
    aes_key = get_random_bytes(16)
    e = CipherHandler(rsa_key, aes_key)
    dados = msg.split()
    salt = get_random_bytes(16)
    enc_text = e.e_protocol(msg)
    key = RSA.generate(2048)
    nonce, enc_key, hash = store_private_key(salt, key, dados[4])
    sign = request(0, dados[2], key.public_key().export_key(), key)
    cert = certificate_dj("registrar", dados[1], key.public_key().export_key(), "BR", dados[2], "clients", sign)
    send(enc_text, client)
    client.close()
    return salt, nonce, enc_key, hash, cert
