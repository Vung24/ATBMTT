import random
import math
import hashlib

def is_prime(n):
    if n == 2 or n == 3:
        return True
    if n == 1 or n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def gcd(a: int, b: int):
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a: int, m: int):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def generate_key(p):
    if not is_prime(p):
        return None, None, None
    # Chọn g ngẫu nhiên trong [2, p-2] và đảm bảo gcd(g, p-1) == 1
    g = random.randint(2, p-2)
    while gcd(g, p-1) != 1:
        g = random.randint(2, p-2)
    # Chọn x ngẫu nhiên trong [1, p-2]
    x = random.randint(1, p-2)
    # Tính y = g^x mod p
    y = pow(g, x, p)
    return (p, g, y), (p, g, x)

# Tạo khóa với p lớn hơn
PUBLIC_KEY = None
PRIVATE_KEY = None
p = 1
while (PUBLIC_KEY is None) or (PRIVATE_KEY is None):
    p = random.randint(1000000, 9999999)  # Tăng lên phạm vi 10000-99999
    while not is_prime(p):
        p = random.randint(1000000, 9999999)
    PUBLIC_KEY, PRIVATE_KEY = generate_key(p)

print(f"PUBLIC_KEY=(p={PUBLIC_KEY[0]}, g={PUBLIC_KEY[1]}, y={PUBLIC_KEY[2]})")
print(f"PRIVATE_KEY=(p={PRIVATE_KEY[0]}, g={PRIVATE_KEY[1]}, x={PRIVATE_KEY[2]})")