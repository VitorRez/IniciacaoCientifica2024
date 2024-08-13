import socket
import threading
from entities.election_manager import election_manager

HEADER = 4096
PORT = 5045
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

def handle_client(conn, addr, election_manager):
    print(f"[NEW CONNECTION] {addr} connected.")
    msg = get_msg(conn, addr)
    if msg != DISCONNECT_MESSAGE:
        data = msg.split()
        if int(data[0]) == 0:
            election_manager.create_election(int(data[1]), int(data[2]))
        else:
            election_manager.create_offices(data[1], int(data[2]), int(data[3]))
    else:
        conn.close()
        return

def get_msg(conn, addr):
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            data = msg.decode(FORMAT)
            return data

class server_election():
    def __init__(self, election_manager):
        self.election_manager = election_manager

    def start_election(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f"[LISTENING] Election manager is listening on {SERVER}")
        try:
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, self.election_manager))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
        finally:
            print("[SERVER CLOSED]")
