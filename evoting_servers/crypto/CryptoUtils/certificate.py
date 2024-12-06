from .hash import *
from .keys import *
import datetime

#information signed with a certifying authority key used to verify the document
def request(version, subject_name, subject_key):
    request = f"version: {version}\nsubject name: {subject_name}\nsubject public key: {subject_key}"
    return create_hash(request)

#creates a x509 certificate
def create_certificate(version, issuer_name, subject_name, subject_key, algorithm,
                       country, state, id, local, signed_request):
    filename = f"{local}certificate_{id}.pem"
    with open(filename, "w") as cert:
        current_time = datetime.datetime.now()
        cert.write(f'Certificate:\n')
        cert.write(f'    Data:\n')
        cert.write(f'       Version: {version}\n')
        cert.write(f'       Serial number:\n')
        cert.write(f'       Signature Algorithm: {algorithm}\n')
        cert.write(f'       Issuer: C={country}, O={issuer_name}\n')
        cert.write(f'       Validity:\n')
        cert.write(f'           Not Before: {current_time.month} {current_time.day} {current_time.hour}:{current_time.minute}:{current_time.second} {current_time.year}\n')
        cert.write(f'           Not After: {current_time.month} {current_time.day} {current_time.hour}:{current_time.minute}:{current_time.second} {current_time.year+1}\n')
        cert.write(f'       Subject: C={country}, ST={state}, O={subject_name}\n')
        cert.write(f'       Subject Public Key Info:\n')
        cert.write(f'           Public key algorithm: NTRU\n')
        cert.write(f'           Public key: (2048 bit)\n')
        cert.write(f'           Pub:\n')
        cert.write(f'               {subject_key}\n')
        cert.write(f'    Signature Algorithm: {algorithm}\n')
        cert.write(f'        {signed_request}\n') 

def create_digital_certificate(version, issuer_name, subject_name, subject_key, algorithm,
                               country, state, signed_request):
    current_time = datetime.datetime.now()
    return(
        f'Certificate:\n'+
        f'     Data:\n'+
        f'       Version: {version}\n'+
        f'       Serial number:\n'+
        f'       Signature Algorithm: {algorithm}\n'+
        f'       Issuer: C={country}, O={issuer_name}\n'+
        f'       Validity:\n'+
        f'           Not Before: {current_time.month} {current_time.day} {current_time.hour}:{current_time.minute}:{current_time.second} {current_time.year}\n'+
        f'           Not After: {current_time.month} {current_time.day} {current_time.hour}:{current_time.minute}:{current_time.second} {current_time.year+1}\n'+
        f'       Subject: C={country}, ST={state}, O={subject_name}\n'+
        f'       Subject Public Key Info:\n'+
        f'           Public key: (2048 bit)\n'+
        f'           Pub:\n'+
        f'               {subject_key}\n'+
        f'    Signature Algorithm: {algorithm}\n'+
        f'        {signed_request}\n'
    )

#extracts public key fromm x509 certificate
def fget_pub_key(certificate_file):
    with open(certificate_file, 'r') as file:
        text = file.read() 
        text = text.split("Pub:\n               ")
        text = text[1].split("Signature")
        return import_key(text[0])
    
def get_pub_key(certificate):
    text = certificate.split("Pub:\n               ")
    text = text[1].split("Signature")
    return import_key(text[0])

