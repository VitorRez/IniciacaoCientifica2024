from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from api.credentials import *
from api.ballots import *
from flask import Flask, request, jsonify
import base64
import requests

app = Flask(__name__)

keys = generate()

priv_key = keys['private_key']
pub_key = keys['public_key']
aes_key = get_random_bytes(16)

VAL_URL = "http://0.0.0.0:5002"


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
    
@app.route('/cast_ballot', methods=['POST'])
def castBallot():
    signed_ballot = request.json['signed_ballot']
    enc_ballot = request.json['enc_ballot']
    enc_credential = request.json['enc_credential']
    enc_electionid = request.json['enc_electionid']

    credential = decrypt_hybrid(enc_credential, priv_key)
    electionid = decrypt_hybrid(enc_electionid, priv_key)

    response = requests.get(f"{VAL_URL}/receive_pub_key")
    
    if response.status_code != 200:
        return response.json()
    
    pub_key_v = import_key(response.json()['key'])

    if not verify(pub_key_v, enc_ballot, signed_ballot):
        return {"success": False, "error": "Validator signature not valid."}
    
    if check_credential_exists(credential, electionid)['success']:
        create_ballot(electionid, enc_ballot)

    return {"success": True, "message": "ballot successfully casted."}
    
app.run(host='0.0.0.0', port=5003)
