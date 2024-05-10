from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class CipherHandler:
    
    def __init__(self, rsa_key, aes_key):
        self.rsa_key = rsa_key
        self.aes_key = aes_key

    def encrypt_sym(self, msg):
        cipher = AES.new(self.aes_key, AES.MODE_EAX)
        nonce = cipher.nonce
        if type(msg) == bytes:
            ciphertext, tag = cipher.encrypt_and_digest(msg)
        else:
            ciphertext, tag = cipher.encrypt_and_digest(msg.encode('utf-8'))
        return (nonce, ciphertext)

    def decrypt_sym(self, nonce, ciphertext, key):
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        msg = cipher.decrypt(ciphertext)
        if type(msg) != bytes:
            msg = bytes.decode(msg)
        return msg

    def encrypt(self, msg):
        key = self.rsa_key
        cipher = PKCS1_OAEP.new(key)
        ciphertext = cipher.encrypt(msg)
        return ciphertext

    def decrypt(self, ciphertext, rsa_key):
        key = RSA.import_key(rsa_key)
        cipher = PKCS1_OAEP.new(key)
        msg = cipher.decrypt(ciphertext)
        return msg

    def e_protocol(self, msg):
        enc = self.encrypt_sym(msg)
        enc_rsa = self.encrypt(self.aes_key)
        return (enc[0], enc[1], enc_rsa)
    
    def d_protocol(self, nonce, cipher_text, aes_enc, rsa_key):
        aes_key = self.decrypt(aes_enc, rsa_key)
        msg = self.decrypt_sym(nonce, cipher_text, aes_key)
        return msg

#msg = 'banana'
#rsa_key = RSA.generate(1024)
#aes_key = get_random_bytes(16)
#e = Cipher(RSA.import_key(rsa_key.public_key().export_key()), aes_key)
#nonce, cipher, enc_aes = e.e_protocol(msg)
#print(cipher)
#plaintext = e.d_protocol(nonce, cipher, enc_aes, rsa_key.export_key('PEM'))
#print(plaintext)