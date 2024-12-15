from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from data_base.sql_manager import *
import socket
import threading

HEADER = 16384
PORT = 5053
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

class tallier_server():
    def __init__(self):
        self.key = generate()

    def send(self, message, client):
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

    def parse_message(self, message):
        print(message.split(': '))
        header, content = message.split(': ')
        return header, content

    def create_random_string(self, size):
        s = string.ascii_uppercase + string.digits
        return ''.join(random.choices(s, k=size))

    def handle_client(self, conn, addr):
        print(f'[NEW CONNECTION ON TALLIER] {addr} connected.')

        priv_key = self.key['private_key']
        pub_key_s = self.key['public_key']
        aes_key = get_random_bytes(16)

        conn.send(pub_key_s)
        pub_key_t = self.get_msg(conn)

        enc_text = self.get_msg(conn)
        text = decrypt_hybrid(enc_text, priv_key).decode('utf-8')

        if text == 'create_credential':
            enc_data = self.get_msg(conn)
            data = pickle.loads(decrypt_hybrid(enc_data, priv_key))

            credential = self.create_random_string(256).encode()
            salt = get_random_bytes(16)

            msg = create_credential(data[0], data[1], credential)
            create_salt(data[0], data[1], salt)

            conn.send(msg.encode('utf-8'))

    def get_msg(self, conn):
        connected = True
        while connected:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length)
                return msg
            
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(ADDR)
        server.listen()
        print(f'[LISTENING] Server is listening on {SERVER}')
        try:
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                print(f'[ACTIVE CONNECTIONS] {threading.active_count()}')
        finally:
            print('[SERVER CLOSED]')
