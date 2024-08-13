import socket
from .crypto.ciphers import *
from .crypto.sign import *
from .key_manager import *

HEADER = 4096
PORT = 5055
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
    

#info = cpf, election, officeid, campaignid
def send_to_adm(info, priv_rsa_key, pub_rsa_key):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    adm_rsa_key = RSA.import_key(client.recv(2048))
    aes_key = get_random_bytes(16)
    e = CipherHandler(adm_rsa_key, aes_key)
    s = signature(priv_rsa_key)
    sign = s.sign(info)
    enc_text = e.e_protocol(info)
    enc_text_s = e.e_protocol(sign)
    send(enc_text, client)
    send(enc_text_s, client)
    send(pub_rsa_key, client)
    client.close()
