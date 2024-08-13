from entities.registrar import *
from crypto.ciphers import *
import socket
import threading

HEADER = 2048
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

def handle_client(conn, addr, reg):
    print(f"[NEW CONNECTION] {addr} connected.")
    chave_pub = reg.key.public_key().export_key()
    conn.send(chave_pub)
    chave_rsa = reg.key.export_key('PEM')
    chave_aes = get_random_bytes(16)
    e_reg = CipherHandler(chave_rsa, chave_aes)
    enc_text = get_msg(conn, addr)
    if enc_text != DISCONNECT_MESSAGE:
        text = e_reg.d_protocol(enc_text, e_reg.rsa_key)
        dados = text.split()
        if dados[0] == b'0':
            reg.voter_registration(dados[1].decode(FORMAT),
                                   dados[2].decode(FORMAT),
                                   dados[3].decode(FORMAT))
        else:
            reg.voter_authentication(dados[2].decode(FORMAT),
                                     dados[3].decode(FORMAT))

    conn.close()

def get_msg(conn, addr):
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            return msg
    
class server_reg():
    def __init__(self, reg):
        self.reg = reg

    def start_reg(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f"[LISTENING] Registrar server is listerning on {SERVER}")
        try:
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, self.reg))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        finally:
            print("[SERVER CLOSED]")

