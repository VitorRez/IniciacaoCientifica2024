from Crypto.Hash import SHA256

def create_hash(text):
    if isinstance(text, str):
        text = text.encode('utf-8')  # Converte string para bytes
    thash = SHA256.new(text)
    return thash.digest()

def verify_hash(text, t_hash):
    if isinstance(text, str):
        text = text.encode('utf-8')  # Converte string para bytes
    t_hash1 = SHA256.new(text)
    return t_hash == t_hash1.digest()
