from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class signature:
    def __init__(self, key):
        self.key = RSA.importKey(key)

    def sign(self, message):
        message_h = SHA256.new(str.encode(message))
        s = pkcs1_15.new(self.key).sign(message_h)
        return s
    
    def verify(self, message, signature, key):
        if type(message) == bytes:
            message_h = SHA256.new(message)
        else:
            message_h = SHA256.new(str.encode(message))
        try:
            pkcs1_15.new(key).verify(message_h, signature)
            print("Valid signature.")
            return True
        except(ValueError, TypeError):
            print("Signature does not match.")
            return False