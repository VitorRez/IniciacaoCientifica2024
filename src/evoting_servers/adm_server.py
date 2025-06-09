from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from flask import Flask, request, jsonify
from api.elections import *
from api.offices import *
from api.candidates import *
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

@app.route('/get_elections', methods=['GET'])
def getElections():
    result = get_elections()

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400

@app.route('/create_election', methods=['POST'])
def createElection():
    enc_data = request.json['message']
    end_setting, end_election, description = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = create_election(end_setting, end_election, description)
    
    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/update_election', methods=['POST'])
def updateElection():
    enc_data = request.json['message']
    electionid, end_setting, end_election, description = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = update_election(electionid, end_setting, end_election, description)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/delete_election', methods=['POST'])
def deleteElection():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key)

    result = delete_election(electionid)
    
    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/create_office', methods=['POST'])
def createOffice():
    enc_data = request.json['message']
    office_name, electionid = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = create_office(office_name, electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/delete_office', methods=['POST'])
def deleteOffices():
    enc_data = request.json['message']
    electionid, office_name = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = delete_office(office_name, electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/create_candidate', methods=['POST'])
def createCandidate():
    pub_key_c = import_key(request.json['key'])
    enc_data = request.json['enc_data']
    enc_signed_data = request.json['enc_signed_data']

    signed_data = decrypt_hybrid(enc_signed_data, priv_key)
    pickled_data = decrypt_hybrid(enc_data, priv_key)
    
    if verify(pub_key_c, pickled_data, signed_data):
        cpf, electionid, office = pickle.loads(pickled_data)

        result = create_candidate(cpf, electionid, office)
        
        if result["success"]:
            return jsonify(result), 200

        else:
            return jsonify(result), 400
        
    else:
        return jsonify({"success": False, "error": "invalid password."}), 400

@app.route('/get_candidates', methods=['POST'])
def getCandidates():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key)

    result = get_candidates(electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/approve_candidate', methods=['POST'])
def approveCandidate():
    enc_data = request.json['message']
    cpf, electionid, office_name = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = approve_candidate(cpf, electionid, office_name)

    if result["success"]:
        return jsonify(result), 200
    
    else:
        return jsonify(result), 200

    
    
@app.route('/get_offices', methods=['GET'])
def getOffices():
    result = get_offices()

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_offices_by_election', methods=['POST'])
def getOfficesByElection():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key)

    result = get_offices_by_election(electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_election', methods=['POST'])
def getElection():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key)

    result = get_election(electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400


app.run(host='0.0.0.0', port=5000)