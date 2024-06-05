import socket
from crypto.ciphers import *
from crypto.PBKDF import *
from data_base.sql_manager import *
from data_base.key_manager import *
from certificates.certifying_authority import *
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

HEADER = 2048
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(msg):
    message = msg
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def registration(info, e):
    enc_text = e.e_protocol(info)
    send(enc_text)
    print(client.recv(HEADER).decode(FORMAT))

def authentication(info, password, e):
    salt = get_random_bytes(16)
    dados = info.split()
    store_salt(f"clients/{dados[1]}", salt)
    enc_text = e.e_protocol(info)
    key = RSA.generate(2048)
    store_private_key(f"clients/{dados[1]}", key, password)
    sign = request(0, dados[0], key.public_key().export_key(), key)
    certificate("registrar", dados[0], key.public_key().export_key(), "BR", dados[1], "clients", sign)
    send(enc_text)
    send(key.public_key().export_key())
    print(client.recv(2048).decode(FORMAT))

def send_to_reg(nome, cpf, unidade):
    client.connect(ADDR)
    rsa_key = RSA.import_key(client.recv(2048))
    aes_key = get_random_bytes(16)
    e = CipherHandler(rsa_key, aes_key)
    info = nome + " " + cpf + " " + unidade
    msg = input("[REGISTERING: 0, AUTHENTICATION: 1]: ")
    send(msg.encode(FORMAT))
    if msg == "0":
        registration(info, e)
    if msg == "1":
        password = input("Create a password: ")
        authentication(info, password, e)
