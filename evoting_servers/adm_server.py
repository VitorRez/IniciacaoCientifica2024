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

@app.route('/receive_pub_key', methods=['GET'])
def receive_pub_key():
    pub_key_base64 = base64.b64encode(pub_key).decode('utf-8')
    return jsonify({'success': True, 'key': pub_key_base64}), 200

@app.route('/election_setting', methods=['POST'])
def election_setting():
    enc_data = base64.b64decode(request.json['message'])
    data = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = create_election(data[0], data[1])
    header, message = parse_message(result)

    if header == 'success':
        return jsonify({'message': result}), 200
    
    else:
        return jsonify({'error': result}), 400
    
@app.route('/office_setting', methods=['POST'])
def office_setting():
    enc_data = base64.b64decode(request.json['message'])
    data = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = create_offices(data[0], data[1], data[2])
    header, message = parse_message(result)

    if header == 'success':
        return jsonify({'message': result}), 200
    
    else:
        return jsonify({'error': result}), 400
    
@app.route('/applying', methods=['POST'])
def applying():
    pub_key_c = base64.b64decode(request.json['key'])
    enc_data = base64.b64decode(request.json['enc_data'])
    enc_signed_data = base64.b64decode(request.json['enc_signed_data'])

    signed_data = decrypt_hybrid(enc_signed_data, priv_key)
    pickled_data = decrypt_hybrid(enc_data, priv_key)
    
    if verify(pub_key_c, pickled_data, signed_data):
        data = pickle.loads(pickled_data)

        result = reg_candidate(data[0], data[1], data[2], data[3])
        header, message = parse_message(result)

        if header == 'success':
            return jsonify({'message': result}), 200
        
        else:
            return jsonify({'error': result}), 400
        
    else:
        return jsonify({'error': 'Invalid signature!'}), 400
    
app.run(host='0.0.0.0', port=5000)