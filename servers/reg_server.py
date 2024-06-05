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
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            else:
                print(f"[{addr}] {msg}")
                dados = msg.split()
                if dados[0] == "0":
                    registration(conn, addr, reg, e_reg)
                if dados[0] == "1":
                    authentication(conn, addr, reg, e_reg)

    conn.close()

def registration(conn, addr, reg, e_reg):
    print("[THE CLIENT WILL REGISTER AS A VOTER]")
    enc_text = get_msg(conn, addr)
    text = e_reg.d_protocol(enc_text, e_reg.rsa_key)
    dados = text.split()
    reg.voter_registration(dados[0].decode('utf-8'), dados[1].decode('utf-8'), dados[2].decode('utf-8'))
    conn.send("Voter registered.".encode(FORMAT))

def authentication(conn, addr, reg, e_reg):
    print("[THE CLIENT WILL REGISTER A PAIR OF KEYS]")
    enc_text = get_msg(conn, addr)
    text = e_reg.d_protocol(enc_text, e_reg.rsa_key)
    dados = text.split()
    key = RSA.import_key(get_msg(conn, addr))
    reg.voter_authentication(dados[1].decode('utf-8'), dados[2].decode('utf-8'))
    conn.send("Voter authenticated.".encode(FORMAT))

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
