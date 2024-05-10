import socket
from crypto.ciphers import *
from crypto.sign import *
from data_base.sql_manager import *
from data_base.key_manager import *

HEADER = 4096
PORT = 5055
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#função para enviar uma mensagem para o servidor do administrador
def send(msg):
    message = msg
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

#envia os dados do eleitor juntamente com os dados assinados para a verificação
#durante a etapa de candidatura
def send_to_adm(nome, cpf, unidade, cargo, id):
    client.connect(ADDR)
    password = input("password: ")
    chave_rsa = RSA.import_key(client.recv(2048))
    chave_rsa_priv = search_private_key(f"clients/{cpf}", password)
    if chave_rsa_priv != None:
        chave_rsa_pub = search_public_key(cpf, "clients").export_key()
        chave_aes = get_random_bytes(16)
        e = CipherHandler(chave_rsa, chave_aes)
        s = signature(chave_rsa_priv)
        info = nome + " " + cpf + " " + unidade + " " + cargo + " " + id
        sign = s.sign(info)
        nonce, cipher, enc_aes = e.e_protocol(info)
        nonce_s, cipher_s, enc_aes_s = e.e_protocol(sign)
        send(nonce)
        send(cipher)
        send(enc_aes)
        send(nonce_s)
        send(cipher_s)
        send(enc_aes_s)
        send(chave_rsa_pub)
        print(client.recv(2048).decode(FORMAT))
    else:
        print("Invalid password.")

