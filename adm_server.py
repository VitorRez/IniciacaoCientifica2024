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
    adm_pub_key = adm.key.public_key().export_key()
    conn.send(adm_pub_key)
    adm_rsa_key = adm.key.export_key('PEM')
    adm_aes_key = get_random_bytes(16)
    e_adm = CipherHandler(adm_rsa_key, adm_aes_key)
    s_adm = signature(adm_rsa_key)
    enc_text = get_msg(conn, addr)
    enc_text_s = get_msg(conn, addr)
    text = e_adm.d_protocol(enc_text, e_adm.rsa_key)
    data = text.split()
    print(data)
    if search_voter(data[0].decode(FORMAT), data[1].decode(FORMAT)):
        print(1)
        text_s = e_adm.d_protocol(enc_text_s, e_adm.rsa_key)
        voter_key = RSA.import_key(get_msg(conn, addr))
        if s_adm.verify(text, text_s, voter_key):
            adm.apply(data[0].decode(FORMAT), data[1].decode(FORMAT), data[2].decode(FORMAT), data[3].decode(FORMAT))
        conn.close()
    else:
        conn.close()

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
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        finally:
            print("[SERVER CLOSED]")