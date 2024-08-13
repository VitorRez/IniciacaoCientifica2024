from Crypto.PublicKey import RSA
from Crypto.Signature import *
from Crypto.Hash import SHA256
from Crypto import *
import datetime

#gera o request de um certificado, esse request é a informação que será encriptada para verificar
#a autenticidade de um certificado x509
def request(version, subject_name, subjectPKInfo, issuerPriKey):
    request = "version: %d\nsubject_name: %s\nsubjectPKInfo: %s\n"%(version, subject_name, subjectPKInfo)
    request_b = str.encode(request)
    h = SHA256.new(request_b)
    #print(request)
    signature = pkcs1_15.new(issuerPriKey).sign(h)
    return signature

def certificate_dj(issuer_name, sub_name, sub_pubkey, sub_country, id, local, signature):
    current_time = datetime.datetime.now()
    issuer_country = "BR"
    text = ("Certificate:\n"+
            "   Data:\n"+
            "       Version:\n"+
            "        Serial number:\n"+
            "        Signature Algorithm: sha256WithRSAEncryption\n"+
            "        Issuer: C=%s, O=%s\n"%(issuer_country, issuer_name)+
            "        Validity:\n"+
            "            Not Before: %d %d %d:%d:%d %d\n"%(current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second, current_time.year)+
            "            Not After: %d %d %d:%d:%d %d\n"%(current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second, current_time.year+1)+
            "        Subject: C=%s, ST=MG, O=%s\n"%(sub_country, sub_name)+
            "        Subject Public Key Info:\n "+
            "            Public key algorithm: RSA\n    Public-key: (2048 bit)\n"+
            "            Public-key: (2048 bit)\n"+
            "            pub:\n"+
            "            %s\n"%(sub_pubkey.decode())+
            "    Signature Algorithm: sha256WithRSAEncryption\n"+
            "        %s\n"%(signature))
    return text


#gera o certificado x509 de um eleitor ou entidade
def certificate(issuer_name, sub_name, sub_pubkey, sub_country, id, local, signature):
    filename = f"{local}/certificate_{id}.pem"
    with open(filename, "w") as cert:
        current_time = datetime.datetime.now()
        issuer_country = "BR"
        cert.write("Certificate:\n")
        cert.write("    Data:\n")
        cert.write("        Version:\n")
        cert.write("        Serial number:\n")
        cert.write("        Signature Algorithm: sha256WithRSAEncryption\n")
        cert.write("        Issuer: C=%s, O=%s\n"%(issuer_country, issuer_name))
        cert.write("        Validity:\n")
        cert.write("            Not Before: %d %d %d:%d:%d %d\n"%(current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second, current_time.year))
        cert.write("            Not After: %d %d %d:%d:%d %d\n"%(current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second, current_time.year+1))
        cert.write("        Subject: C=%s, ST=MG, O=%s\n"%(sub_country, sub_name))
        cert.write("        Subject Public Key Info:\n ")
        cert.write("            Public key algorithm: RSA\n    Public-key: (2048 bit)\n")
        cert.write("            Public-key: (2048 bit)\n")
        cert.write("            pub:\n")
        cert.write("            %s\n"%(sub_pubkey.decode()))
        cert.write("    Signature Algorithm: sha256WithRSAEncryption\n")
        cert.write("        %s\n"%(signature))

#gera as requests e os certificados das principais entidade da etapa de pre eleição
def autoridade_certificadora(aut, reg, adm, val, tal):
    sign_aut_req = request(0, "certifying_authority",aut.key.public_key().export_key("PEM"), aut.key)
    sign_reg_req = request(1, 'registrar', reg.key.public_key().export_key("PEM"), reg.key)
    sign_adm_req = request(2, 'adiminstrador', adm.key.public_key().export_key("PEM"), adm.key)
    sign_val_req = request(3, 'validator', val.key.public_key().export_key("PEM"), val.key)
    sign_tal_req = request(4, 'tallier', tal.key.public_key().export_key("PEM"), tal.key)
    certificate('autoridade_certificadora', 'autoridade_certificadora', aut.key.public_key().export_key("PEM"), "BR", "aut", "certificates", sign_aut_req)
    certificate('autoridade_certificadora', 'registrar', reg.key.publickey().exportKey("PEM"), "BR", "reg", "certificates", sign_reg_req)
    certificate('autoridade_certificadora', 'adminstrador', adm.key.publickey().exportKey("PEM"), "BR", "adm", "certificates", sign_adm_req)
    certificate('autoridade_certificadora', 'validator', val.key.publickey().exportKey("PEM"), "BR", "val", "certificates", sign_val_req)
    certificate('autoridade_certificadora', 'tallier', tal.key.publickey().exportKey("PEM"), "BR", "tal", "certificates", sign_tal_req)
