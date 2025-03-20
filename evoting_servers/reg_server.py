from crypto.CryptoUtils.encrypt_sym import *
from crypto.CryptoUtils.hash import *
from crypto.CryptoUtils.keys import *
from crypto.CryptoUtils.PBKDF import *
from crypto.encrypt_hybrid import *
from crypto.key_manager import *
from crypto.PyNTRU.NTRU import *
from api.voters import *
from api.elections import *
from api.users import *
from api.candidates import *
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

@app.route('/create_voter', methods=['POST'])
def createVoter():
    enc_data = request.json['message']
    name, cpf, electionid = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = create_voter(name, cpf, electionid)
    
    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/create_user', methods=['POST'])
def createUser():
    enc_data = request.json['message']
    name, cpf, password = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = create_user(cpf, name, password, 0)
    
    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/delete_voter', methods=['POST'])
def deleteVoter():
    enc_data = request.json['message']
    cpf, electionid = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = delete_voter(cpf, electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_voter', methods=['POST'])
def getVoter():
    enc_data = request.json['message']
    cpf, electionid = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    result = get_voter(cpf, electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_voters', methods=['GET'])
def getVoters():
    result = get_voters()

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_users', methods=['GET'])
def getUsers():
    result = get_users()

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_user', methods=['POST'])
def getUser():
    enc_data = request.json['message']
    cpf = decrypt_hybrid(enc_data, priv_key)

    result = get_user(cpf)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400

@app.route('/get_voters_by_cpf', methods=['POST'])
def getVotersByCpf():
    enc_data = request.json['message']
    cpf = decrypt_hybrid(enc_data, priv_key)

    result = get_voters_by_cpf(cpf)
    
    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/get_voters_by_election', methods=['POST'])
def getVotersByElection():
    enc_data = request.json['message']
    electionid = decrypt_hybrid(enc_data, priv_key).decode('utf-8')

    result = get_voters_by_election(electionid)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400
    
@app.route('/update_voter', methods=['POST'])
def updateVoter():
    enc_data = request.json['messsage']
    cpf, name, electionid, auth, candidate, pub_key, priv_key, salt =  pickle.loads(decrypt_hybrid(enc_data, priv_key))

    
    result = update_voter(cpf, name, electionid, auth, candidate, pub_key, priv_key, salt)

    if result["success"]:
        return jsonify(result), 200

    else:
        return jsonify(result), 400

    
@app.route('/authentication', methods=['POST'])
def authentication():
    enc_data = request.json['message']
    name, cpf, electionid, version, public_key_c, priv_key_c, salt = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    req = make_request(version, name, public_key_c)
    signed_req = sign(priv_key, pub_key, req)
    certificate = create_digital_certificate(version, 'Registrar', name, public_key_c, 'SHA256WithNTRU', 'BR', 'MG', signed_req)

    TAL_URL = "http://0.0.0.0:5003"

    try:
        response = requests.get(f"{TAL_URL}/receive_pub_key")

        if response.status_code == 200:
            pub_key_t = import_key(response.json()['key'])

            enc_data = encrypt_hybrid(electionid, pub_key_t, aes_key)

            response = requests.post(f"{TAL_URL}/create_credential", json={'message': enc_data})

            if response.status_code == 200:
                update_voter(cpf, name, electionid, 1, 0, certificate, priv_key_c, salt)

                return jsonify({"success": True, "message": "Voter successfully authenticated!"}), 200
            
            else:
                return jsonify({"success": False, "error": "coundn't generate certificate, try again later."}), 400
            
        else:
            return jsonify({"success": False, "error": "couldn't access tallier server."}), 400
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    
@app.route('/applying', methods=['POST'])
def applying():
    enc_data = request.json['message']
    cpf, electionid, office_name = pickle.loads(decrypt_hybrid(enc_data, priv_key))

    voter = get_voter(cpf, electionid)['data']

    result = update_voter(voter['cpf'], voter['name'], voter['electionid'], voter['auth'], 1, voter['pub_key'], voter['priv_key'], voter['salt'])
    if result['success']:
        result = create_candidate(cpf, electionid, office_name)

        if result['success']:
            return jsonify({"success": True, "message": "ok"}), 200
        else:
            return jsonify({"success": False, "message": "Couldn't create candidate."}), 400
        
    else:
        return jsonify({"success": False, "message": "Couldn't update voter."}), 400


app.run(host='0.0.0.0', port=5001)