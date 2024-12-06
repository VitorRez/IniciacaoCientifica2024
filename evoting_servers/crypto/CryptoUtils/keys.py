import base64

def export_key(key, type='public'):

    key_64 = base64.encodebytes(key).decode('utf-8')

    if type == 'public':
        pem_key = f'-----BEGIN PUBLIC KEY-----{key_64}-----END PUBLIC KEY-----'
    else:
        pem_key = f'-----BEGIN PRIVATE KEY-----{key_64}-----END PRIVATE KEY-----'

    return pem_key

def import_key(pem_data, type='public'):
    
    if type == 'public':
        pem_body = pem_data.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").strip()

    else:
        pem_body = pem_data.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").strip()  

    key_bytes = base64.decodebytes(pem_body.encode('utf-8'))
    return key_bytes