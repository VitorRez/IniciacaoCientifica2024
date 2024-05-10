import socket
from crypto.ciphers import *
from crypto.PBKDF import *
from data_base.old_code.database_manager import *
from data_base.key_manager import *
from certificates.certifying_authority import *
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

msg = 'teste'
rsa_key = RSA.generate(1024)
aes_key = get_random_bytes(16)
e = CipherHandler(RSA.import_key(rsa_key.public_key().export_key()), aes_key)
nonce, cipher, enc_aes = e.e_protocol(msg)
print(cipher)
plaintext = e.d_protocol(nonce, cipher, enc_aes, rsa_key.export_key('PEM'))
print(plaintext)