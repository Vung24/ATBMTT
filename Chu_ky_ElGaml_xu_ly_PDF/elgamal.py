from Crypto.Random import random
from Crypto.Util import number
import hashlib

def generate_keys_elgamal():
    p = number.getPrime(512)
    g = random.randint(2, p - 1)
    x = random.randint(1, p - 2)
    y = pow(g, x, p)
    private_key = (p, g, x)
    public_key = (p, g, y)
    return private_key, public_key

def sign_data_elgamal(data, private_key, hash_function):
    p, g, x = private_key
    hash_value = hashlib.new(hash_function, data.encode("utf-8")).hexdigest()
    m = int(hash_value, 16) % p
    k = random.randint(1, p - 2)
    while number.GCD(k, p - 1) != 1:
        k = random.randint(1, p - 2)
    r = pow(g, k, p)
    s = (m - x * r) * number.inverse(k, p - 1) % (p - 1)
    return r, s

def verify_signature_elgamal(data, signature, public_key, hash_function):
    p, g, y = public_key
    r, s = signature
    if not (1 <= r <= p - 1):
        return False
    hash_value = hashlib.new(hash_function, data.encode("utf-8")).hexdigest()
    m = int(hash_value, 16) % p
    v1 = pow(y, r, p) * pow(r, s, p) % p
    v2 = pow(g, m, p)
    return v1 == v2

# Tạo và in khóa
private_key, public_key = generate_keys_elgamal()
print(f"PUBLIC_KEY=(p={public_key[0]}, g={public_key[1]}, y={public_key[2]})")
print(f"PRIVATE_KEY=(p={private_key[0]}, g={private_key[1]}, x={private_key[2]})")