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
import requests

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

@app.route('/registering', methods=['POST'])
def registering():
    enc_data = base64.b64decode(request.json['message'])
    data = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = reg_voter(data[0], data[1], data[2])
    header, message = parse_message(result)

    if header == 'success':
        return jsonify({'message': result}), 200
    
    else:
        return jsonify({'error': result}), 400
    
@app.route('/authentication', methods=['POST'])
def authentication():
    enc_data = base64.b64decode(request.json['message'])
    data = pickle.loads(decrypt_hybrid(enc_data, priv_key))
    name, cpf, electionid, version, public_key_c = data[0], data[1], data[2], data[3], data[4]

    req = make_request(version, name, public_key_c)
    signed_req = sign(priv_key, pub_key, req)
    certificate = create_digital_certificate(version, 'Registrar', name, public_key_c, 'SHA256WithNTRU', 'BR', 'MG', signed_req)
    
    enc_cert = encrypt_hybrid(certificate, import_key(public_key_c), aes_key)
    enc_cert_base64 = base64.b64encode(enc_cert).decode('utf-8')

    TAL_URL = "http://192.168.68.104:5003"

    try:
        response = requests.get(f"{TAL_URL}/receive_pub_key")
        print(1)

        if response.status_code == 200:
            pub_key_t = base64.b64decode(response.json()['key'])
            print(2)

            data = pickle.dumps([electionid])
            enc_data = encrypt_hybrid(data, pub_key_t, aes_key)
            enc_data_base64 = base64.b64encode(enc_data).decode('utf-8')
            print(3)

            response = requests.post(f"{TAL_URL}/create_credential", json={'message': enc_data_base64})
            print(4)

            if response.status_code == 200:
                print(5.1)
                return jsonify({'success': True, 'certificate': enc_cert_base64}), 200
            
            else:
                print(5.2)
                return jsonify({'error': 'Couldnt generate certificate.'}), 400
            
        else:
            print(5.3)
            return jsonify({'error': 'Couldnt access tallier server.'}), 400
        
    except Exception as e:
        print(5.4)
        return jsonify({'error': e}), 400

app.run(host='0.0.0.0', port=5001)