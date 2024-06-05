from entities.administrator import *
from crypto.sign import *
from crypto.ciphers import *
import socket
import threading

HEADER = 4096
PORT = 5055
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

def handle_client(conn, addr, adm):
    print(f"[NEW CONNECTION] {addr} connected.")
    chave_pub = adm.key.public_key().export_key()
    conn.send(chave_pub)
    chave_rsa = adm.key.export_key('PEM')
    chave_aes = get_random_bytes(16)
    e_adm = CipherHandler(chave_rsa, chave_aes)
    s_adm = signature(chave_rsa)
    enc_text = get_msg(conn, addr)
    enc_text_s = get_msg(conn, addr)
    text = e_adm.d_protocol(enc_text, e_adm.rsa_key)
    dados = text.split()
    if search_voter(dados[1].decode('utf-8'), dados[2].decode('utf-8')):
        text_s = e_adm.d_protocol(enc_text_s, e_adm.rsa_key)
        chave_eleitor = RSA.import_key(get_msg(conn, addr))
        if s_adm.verify(text, text_s, chave_eleitor):
            adm.apply(dados[0].decode('utf-8'), dados[1].decode('utf-8'), dados[2].decode('utf-8'), dados[3].decode('utf-8'), dados[4].decode('utf-8'))
            conn.send("Aproved application.".encode(FORMAT))
        else:
            conn.send("Keys does not match".encode(FORMAT))
            conn.close()
        conn.close()
    else:
        conn.send("Voter not authenticated.".encode(FORMAT))


def get_msg(conn, addr):
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            return msg
        
class server_adm():
    def __init__(self, adm):
        self.adm = adm

    def start_adm(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f"[LISTENING] Administrator server is listening on {SERVER}")
        try:
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, self.adm))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
        finally:
            print("[SERVER CLOSED]")