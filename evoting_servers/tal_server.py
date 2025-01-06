from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from data_base.sql_manager import *
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

keys = generate()

priv_key = keys['private_key']
pub_key = keys['public_key']
aes_key = get_random_bytes(16)

def parse_message(message):
    header, content = message.split(': ')
    return header, content

def create_random_string(size):
    s = string.ascii_uppercase + string.digits
    return ''.join(random.choices(s, k=size))

@app.route('/receive_pub_key', methods=['GET'])
def receive_pub_key():
    pub_key_base64 = base64.b64encode(pub_key).decode('utf-8')
    return jsonify({'success': True, 'key': pub_key_base64}), 200

@app.route('/create_credential', methods=['POST'])
def createCredential():
    enc_data = base64.b64decode(request.json['message'])
    data = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    credential = create_random_string(256).encode()
    salt = get_random_bytes(16)

    result = create_credential(data[0], credential, salt)
    header, message = parse_message(result)

    if header == 'success':
        return jsonify({'message': result}), 200
    
    else:
        return jsonify({'error': result}), 400
    
@app.route('/get_commits', methods=['POST'])
def get_commits():
    pub_key_c = base64.b64decode(request.json['key'])
    enc_data = base64.b64decode(request.json['data'])

    electionids = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    commits = create_commit(electionids)

    enc_data = encrypt_hybrid(pickle.dumps(commits), pub_key_c, aes_key)
    enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')

    return jsonify({'success': True, 'commits': enc_data_base64}), 200
    
app.run(host='0.0.0.0', port=5003)

