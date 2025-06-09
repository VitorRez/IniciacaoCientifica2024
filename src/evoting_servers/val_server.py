from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from api.candidates import *
from api.credentials import *
from api.users import *
from api.voters import *
from flask import Flask, request, jsonify
import base64
import requests

app = Flask(__name__)

keys = generate()

priv_key = keys['private_key']
pub_key = keys['public_key']
aes_key = get_random_bytes(16)

@app.route('/receive_pub_key', methods=['GET'])
def receive_pub_key():
    pub_key_base64 = export_key(pub_key)
    return jsonify({'success': True, 'key': pub_key_base64}), 200

@app.route('/verify_ballot', methods=['POST'])
def verify_ballot():
    enc_ballot = request.json['enc_ballot']

    electionid = decrypt_hybrid(request.json['enc_electionid'], priv_key)
    cpf = decrypt_hybrid(request.json['enc_cpf'], priv_key)
    p_hash = decrypt_hybrid(request.json['enc_password'], priv_key)

    voter = get_voter(cpf, electionid)['data']
    user = get_user(cpf)['data'] 
     
    if voter['voted'] == 1:
        credential = create_random_string(256).encode()

    elif verify_hash_with_hash(p_hash, user['password']):
        credential = get_random_credential(electionid)['data']
        vote(cpf, electionid)
        
    else:
        credential = create_random_string(256).encode()

    TAL_URL = "http://0.0.0.0:5003"

    try:
        response = requests.get(f"{TAL_URL}/receive_pub_key")
        pub_key_t = import_key(response.json()['key'])

        enc_data, ephemeral_key = encrypt_hybrid(credential, pub_key_t, aes_key)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

    signed_ballot = sign(priv_key, pub_key, enc_ballot)

    return jsonify({"success": True, "credential": enc_data, 'signed_ballot': signed_ballot}), 200


app.run(host='0.0.0.0', port=5002)