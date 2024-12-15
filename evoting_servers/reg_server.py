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
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

class registrar_server():
    def __init__(self):
        self.key = generate()

    def send(self, message, client):
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

    def parse_message(self, message):
        header, content = message.split(': ')
        return header, content

    def handle_client(self, conn, addr):
        print(f'[NEW CONNECTION ON REGISTRAR] {addr} connected.')

        priv_key = self.key['private_key']
        pub_key_s = self.key['public_key']
        aes_key = get_random_bytes(16)

        conn.send(pub_key_s)

        enc_text = self.get_msg(conn)
        text = decrypt_hybrid(enc_text, priv_key).decode('utf-8')

        if text == 'registering':
            enc_data = self.get_msg(conn)
            data = pickle.loads(decrypt_hybrid(enc_data, priv_key))
            name, cpf, electionid = data[0], data[1], data[2]

            msg = reg_voter(name, cpf, electionid)

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER, 5053))

            pub_key_t = client.recv(HEADER)
            self.send(pub_key_s, client)

            text = 'create_credential'
            enc_text = encrypt_hybrid(text, pub_key_t, aes_key)
            self.send(enc_text, client)

            text = pickle.dumps([cpf, electionid])
            enc_text = encrypt_hybrid(text, pub_key_t, aes_key)
            self.send(enc_text, client)

            response = self.parse_message(client.recv(HEADER).decode('utf-8'))
            if response[0] == 'error':
                delete_voter(cpf, electionid)
                msg = 'error: failed to register voter!'

            conn.send(msg.encode('utf-8'))

        elif text == 'authentication':
            enc_data = self.get_msg(conn)
            data = pickle.loads(decrypt_hybrid(enc_data, priv_key))
            name, cpf, electionid, version, public_key_c = data[0], data[1], data[2], data[3], data[4]

            req = request(version, name, public_key_c)
            signed_req = sign(priv_key, pub_key_s, req)
            certificate = create_digital_certificate(version, 'Registrar', name, public_key_c, 'SHA256WithNTRU', 'BR', 'MG', signed_req)

            enc_cert = encrypt_hybrid(certificate, import_key(public_key_c), aes_key)
            conn.send(enc_cert)

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