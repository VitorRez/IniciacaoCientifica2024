from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from api.credentials import *
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

keys = generate()

priv_key = keys['private_key']
pub_key = keys['public_key']
aes_key = get_random_bytes(16)


@app.route('/receive_pub_key', methods=['GET'])
def receive_pub_key():
    pub_key_base64 = export_key(pub_key)
    return jsonify({'success': True, 'key': pub_key_base64}), 200

@app.route('/create_credential', methods=['POST'])
def createCredential():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key)

    result = create_credential(electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_commits', methods=['POST'])
def getCommits():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key)

    result = get_commits(electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
app.run(host='0.0.0.0', port=5003)
