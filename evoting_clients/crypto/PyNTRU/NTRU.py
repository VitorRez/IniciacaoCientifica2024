from .NTRUEncrypt import NTRUEncrypt
from .NSS import NSS
from .mathutils import random_poly
from sympy.abc import x
from sympy import ZZ, Poly
import numpy as np
import math
import pickle

def generate(N=256, p=3, q=128, Dmin=55, Dmax=87):
    ntruc = NTRUEncrypt(N, p, q)
    ntruc.generate_random_keys()
    
    g_c = np.array(ntruc.g_poly.all_coeffs()[::-1])
    h_c = np.array(ntruc.h_poly.all_coeffs()[::-1])
    f_c = np.array(ntruc.f_poly.all_coeffs()[::-1])
    f_p_c = np.array(ntruc.f_p_poly.all_coeffs()[::-1])

    ntrus = NSS(N, p, q, Dmin, Dmax)
    ntrus.generate_random_keys()

    g_s = np.array(ntrus.g_poly.all_coeffs()[::-1])
    h_s = np.array(ntrus.h_poly.all_coeffs()[::-1])
    f_s = np.array(ntrus.f_poly.all_coeffs()[::-1])
    
    priv_key = {'N': N, 'p': p, 'q': q, 'f_c': f_c, 'f_p_c': f_p_c, 'g_c': g_c, 'f_s': f_s, 'g_s': g_s, 'Dmin': Dmin, 'Dmax': Dmax}
    pub_key = {'N': N, 'p': p, 'q': q, 'h_c': h_c, 'h_s': h_s, 'Dmin': Dmin, 'Dmax': Dmax}

    return {'private_key': pickle.dumps(priv_key), 'public_key': pickle.dumps(pub_key)}

def encrypt(pub_key, input_str):

    if isinstance(input_str, str):
        input_str = input_str.encode('utf-8')

    input = np.unpackbits(np.frombuffer(input_str, dtype=np.uint8))
    pub_key = pickle.loads(pub_key)
    
    ntru = NTRUEncrypt(int(pub_key['N']), int(pub_key['p']), int(pub_key['q']))
    ntru.h_poly = Poly(pub_key['h_c'].astype(int)[::-1], x).set_domain(ZZ)

    if ntru.N < len(input):
        raise Exception("Input is too large for current N")
    
    output = (ntru.encrypt(Poly(input[::-1], x).set_domain(ZZ),random_poly(ntru.N, int(math.sqrt(ntru.q)))).all_coeffs()[::-1])

    return pickle.dumps(output)

def decrypt(priv_key, input):

    input = pickle.loads(input)
    priv_key = pickle.loads(priv_key)

    ntru = NTRUEncrypt(int(priv_key['N']), int(priv_key['p']), int(priv_key['q']))
    ntru.f_poly = Poly(priv_key['f_c'].astype(int)[::-1], x).set_domain(ZZ)
    ntru.f_p_poly = Poly(priv_key['f_p_c'].astype(int)[::-1], x).set_domain(ZZ)

    if ntru.N < len(input):
        raise Exception("Input is too large for current N")
    
    decrypted = ntru.decrypt(Poly(input[::-1], x).set_domain(ZZ)).all_coeffs()[::-1]

    return (np.packbits(np.array(decrypted).astype(int)).tobytes())

def sign(priv_key, pub_key, input_str):

    if isinstance(input_str, str):
        input_str = input_str.encode('utf-8')

    pub_key = pickle.loads(pub_key)
    priv_key = pickle.loads(priv_key)

    ntru = NSS(int(priv_key['N']), int(priv_key['p']), int(priv_key['q']), int(priv_key['Dmin']), int(priv_key['Dmax']))
    ntru.f_poly = Poly(priv_key['f_s'].astype(int)[::-1], x).set_domain(ZZ)
    ntru.g_poly = Poly(priv_key['g_s'].astype(int)[::-1], x).set_domain(ZZ)
    ntru.h_poly = Poly(pub_key['h_s'].astype(int)[::-1], x).set_domain(ZZ)

    if ntru.N < len(input_str):
        raise Exception("Input is too large for current N")
    
    s = ntru.sign(input_str)
    return pickle.dumps(s.all_coeffs())

def verify(pub_key, input_str, signed_input):

    if isinstance(input_str, str):
        input_str = input_str.encode('utf-8')

    signed_m = pickle.loads(signed_input)
    pub_key = pickle.loads(pub_key)

    ntru = NSS(int(pub_key['N']), int(pub_key['p']), int(pub_key['q']), int(pub_key['Dmin']), int(pub_key['Dmax']))
    ntru.h_poly = Poly(pub_key['h_s'].astype(int)[::-1], x).set_domain(ZZ)
    
    return ntru.verify(input_str, Poly(signed_m, x).set_domain(ZZ))

