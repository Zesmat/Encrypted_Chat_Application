#Resources used:
# https://pyquesthub.com/implementing-rsa-encryption-from-scratch-in-python
# https://www.askpython.com/python/examples/rsa-algorithm-in-python
# https://youtu.be/58LLuy1B8dk?si=IRPy_SZSXUM34_YJ
# https://www.geeksforgeeks.org/dsa/primality-test-set-3-miller-rabin/
# https://www.geeksforgeeks.org/python/python-program-for-basic-and-extended-euclidean-algorithms-2/
# https://www.freecodecamp.org/news/binary-exponentiation-algorithm-explained-with-examples/

import random

# MATHS implementation first to avoid using pow etc.. 
# RSA step 4 relies on the relationship: d ≡ e^(-1) (mod φ(n)). so, to find d, we need to find the modular 
# multiplicative inverse of e modulo φ(n). This can be done using the Extended Euclidean Algorithm.
# which is a method for finding the greatest common divisor (GCD) of two numbers and also provides a way to express the GCD as a  combination of those numbers.
def gcd_extended(a, b):
    
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# calculates e^(-1) (mod φ(n)) mannually 
def mod_inverse(e, phi):
    gcd, x, y = gcd_extended(e, phi)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % phi + phi) % phi

# manually calculates the binary exponentiation (used in both the encryption and decryption steps of RSA) 
# we use this method for efficiently computing large powers of numbers modulo some integer.
# since enc and dec. involve calcualting m^e mod n and c^d mod n
# we can use this efficient way to compute these large powers without running into performance issues or overflow errors.  
def power(base, exp, mod):
    res = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res

# Primality test using Miller-Rabin since the RSA requires 2 prime numbers (p & q) that cannot just be 'guessed' or randomized. 
# Contemplated using the Fermat test ;however, through research I found that the Miller-Rabin test generally more preferred since it cannot be fooled by absolute pseudoprimes (which are composite numbers - not prime) that can be used to satisfy the Fermat test. 
def is_prime(n, k=5):
    
    if n < 2: 
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19]:
        
        if n == p: 
            return True
        if n % p == 0: 
            return False
    
    # writes n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = power(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

#generates a large prime number with the help of the Miller-Rabin method used in the method we used below 
def generate_large_prime(bits):
    while True:
        p = random.getrandbits(bits)
        if is_prime(p):
            return p

# RSA implementation 

def generate_keys(bits):
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537
    d = mod_inverse(e, phi)
    
    return (e, n), (d, n)

def encrypt(message_bytes, public_key):
    e, n = public_key
    # directly converts the raw bytes into the integer m
    m = int.from_bytes(message_bytes, 'big')
    
    # compute the ciphertext c = m^e mod n
    return power(m, e, n)

def decrypt(ciphertext, private_key):
    d, n = private_key
    # computes the decrypted integer m = c^d mod n
    m = power(ciphertext, d, n)
    
    # calculates the byte length and return the raw bytes directly without converting to string first
    byte_length = (m.bit_length() + 7) // 8
    return m.to_bytes(byte_length, 'big')