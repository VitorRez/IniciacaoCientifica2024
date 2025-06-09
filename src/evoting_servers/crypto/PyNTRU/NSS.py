from .mathutils import *
import numpy as np
from sympy.abc import x
from sympy.polys.polyerrors import NotInvertible
from sympy import ZZ, Poly
from Crypto.Hash import SHA256
from random import choice

class NSS:
    N = None
    p = None
    q = None

    f_poly = None
    g_poly = None
    h_poly = None

    R_poly = None
    
    f0_poly = Poly(1, x)
    g0_poly = Poly(1 - 2 * x, x)

    Ff = 70
    Fg = 40
    Fm = 32

    w2_limit = 32
    w1_limit = 25

    Dmin = None
    Dmax = None

    def __init__(self, N, p, q, Dmin, Dmax):
        self.N = N
        self.p = p
        self.q = q
        self.Dmin = Dmin
        self.Dmax = Dmax
        self.R_poly = Poly(x ** N - 1, x).set_domain(ZZ)

    def generate_f(self):

        f1_poly = random_poly(self.N, self.Ff)

        f_poly = self.f0_poly + self.p * f1_poly

        return f_poly
    
    def generate_g(self):

        g1_poly = random_poly(self.N, self.Fg)

        g_poly = self.g0_poly + self.p * g1_poly

        return g_poly
    
    def generate_random_keys(self):
        g_poly = self.generate_g()
        tries = 10
        while tries > 0 and (self.h_poly is None):

            f_poly = self.generate_f()

            try:
                self.generate_public_key(f_poly, g_poly)
            except NotInvertible as ex:
                tries -= 1

        if self.h_poly is None:
            raise Exception("Couldn't generate invertible f")
        
    def generate_public_key(self, f_poly, g_poly):
        self.f_poly = f_poly
        self.g_poly = g_poly

        f_q_poly = invert_poly(self.f_poly, self.R_poly, self.q)

        self.h_poly = (f_q_poly * self.g_poly % self.R_poly).trunc(self.q)

    def hash_message(self, message):
    
        if isinstance(message, np.ndarray):
            message = message.tobytes()

        hash_obj = SHA256.new()
        hash_obj.update(message)

        hash_digest = hash_obj.digest()
        hash_integers = list(np.frombuffer(hash_digest, dtype=np.uint8))[:64]
        hash_integers = [i % 251 for i in hash_integers]

        first_half = hash_integers[:32]
        second_half = hash_integers[32:64]

        coeffs = [(x**e) for e in first_half] + [(-x**e) for e in second_half]

        m_poly = Poly(sum(coeffs, x)).set_domain(ZZ)

        return (m_poly % self.R_poly).trunc(self.p)

    def generate_w2(self):
        w2 = random_poly(self.N, self.w2_limit)
        return w2

    def generate_w1(self, m_poly, w2):

        sl = (self.f_poly * (m_poly + self.p * w2) % self.R_poly).trunc(self.q)
        tl = (self.g_poly * (m_poly + self.p * w2) % self.R_poly).trunc(self.q)

        coeffs = [0] * self.N
        non_zero_count = 0

        for i in range(self.N):
            sl_i = sl.coeffs()[i] if i < len(sl.coeffs()) else 0
            tl_i = tl.coeffs()[i] if i < len(tl.coeffs()) else 0
            m_i = m_poly.coeffs()[i] if i < len(m_poly.coeffs()) else 0

            if sl_i % self.p != m_i % self.p and tl_i % self.p != m_i % self.p and sl_i % self.p == tl_i % self.p:
                coeffs[i] = (m_i - sl_i) % self.p
            elif sl_i % self.p != m_i % self.p and tl_i % self.p != m_i % self.p and sl_i % self.p != tl_i % self.p:
                coeffs[i] = choice([1, -1])
            elif sl_i % self.p != m_i % self.p and tl_i % self.p == m_i % self.p:
                if np.random.rand() < 0.25:
                    coeffs[i] = (m_i - sl_i) % self.p
            elif sl_i % self.p == m_i % self.p and tl_i % self.p != m_i % self.p:
                if np.random.rand() < 0.25:
                    coeffs[i] = (m_i - tl_i) % self.p

            if coeffs[i] != 0:
                non_zero_count += 1

            if non_zero_count > self.w1_limit:
                break
        
        coeffs_2 = [0] * self.N
        for i in range(self.N):
            if np.random.rand() < 1/self.p:
                w1_i = coeffs[i] if i < len(coeffs) else 0
                m_i = m_poly.coeffs()[i] if i < len(m_poly.coeffs()) else 0
                w2_i = w2.coeffs()[i] if i < len(w2.coeffs()) else 0

                coeffs_2[i] = w2_i - m_i - w1_i
            else:
                coeffs_2[i] = w2.coeffs()[i] if i < len(w2.coeffs()) else 0

        w2 = Poly(coeffs_2, x).set_domain(ZZ)
        w1 = Poly(coeffs, x).set_domain(ZZ)

        return w1

    def generate_w(self, m_poly):
        w2 = self.generate_w2()
        w1 = self.generate_w1(m_poly, w2)

        return m_poly + w1 + self.p * w2
    
    def sign(self, msg):
        m_poly = self.hash_message(msg)
        w = self.generate_w(m_poly)
        s = (self.f_poly * w % self.R_poly).trunc(self.q)
        while not self.verify(msg, s):
            w = self.generate_w(m_poly)
            s = (self.f_poly * w % self.R_poly).trunc(self.q)

        return s

    def deviation(self, poly1, poly2):

        max_len = max(len(poly1.all_coeffs()), len(poly1.all_coeffs()))

        coeffs1 = [0] * (max_len - len(poly1.all_coeffs())) + poly1.all_coeffs()
        coeffs2 = [0] * (max_len - len(poly2.all_coeffs())) + poly2.all_coeffs()

        a_q = [(c % self.q - self.q if c % self.q >= self.q/2 else c % self.q) for c in coeffs1]
        b_q = [(c % self.q - self.q if c % self.q >= self.q/2 else c % self.q) for c in coeffs2]

        a_p = [(c % self.p - self.p if c % self.p >= self.p/2 else c % self.p) for c in a_q]
        b_p = [(c % self.p - self.p if c % self.p >= self.p/2 else c % self.p) for c in b_q]

        return sum(1 for a, b in zip(a_p, b_p) if a != b)

    def verify(self, msg, s):
        if s == 0:
            return False
        
        m_poly = self.hash_message(msg)
        
        f0_m = (self.f0_poly * m_poly)
        dev_s_f0_m = self.deviation(s, f0_m)

        if not (self.Dmin <= dev_s_f0_m <= self.Dmax):
            return False

        t = (self.h_poly * s % self.R_poly).trunc(self.q)
        g0_m = (self.g0_poly * m_poly)
        dev_t_g0_m = self.deviation(t, g0_m)

        if not (self.Dmin <= dev_t_g0_m <= self.Dmax):
            return False

        return True