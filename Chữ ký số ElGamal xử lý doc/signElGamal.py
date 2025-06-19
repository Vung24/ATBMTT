import hashlib
import keyElGamal
import random


def get_hash_code(msg_or_file: str, is_file=False):
    """Tính giá trị băm SHA-256 của thông điệp hoặc file."""
    sha256 = hashlib.sha256()
    if is_file:
        with open(msg_or_file, "rb") as f:
            # Đọc file theo khối để xử lý file lớn
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
    else:
        sha256.update(msg_or_file.encode('utf-8'))
    # Chuyển giá trị băm hex thành số nguyên
    hash_code = int(sha256.hexdigest(), 16) % (keyElGamal.PRIVATE_KEY[0] - 1)
    return hash_code


def sign(msg_or_file, is_file=False):
    try:
        # Tính giá trị băm SHA-256, tạo chữ ký sign
        hash_code = get_hash_code(msg_or_file, is_file)
        p, g, x = keyElGamal.PRIVATE_KEY
        # Chọn k ngẫu nhiên sao cho gcd(k, p-1) = 1
        k = random.randint(1, p - 2)
        while keyElGamal.gcd(k, p - 1) != 1:
            k = random.randint(1, p - 2)

        # Tính r = g^k mod p
        r = pow(g, k, p)
        # Tính s = k^(-1) * (hash_code - x * r) mod (p-1)
        k_inv = keyElGamal.mod_inverse(k, p - 1)
        if k_inv is None:
            return None
        s = (k_inv * (hash_code - x * r)) % (p - 1)

        return f"{r}-{s}"
    except Exception as e:
        print(f"Lỗi khi ký: {e}")
        return None


def verify(msg_or_file, sign_code, is_file=False):
    try:
        # Tính lại giá trị băm SHA-256
        hash_code = get_hash_code(msg_or_file, is_file)
        p, g, y = keyElGamal.PUBLIC_KEY
        # Tách r và s từ chữ ký
        r, s = map(int, sign_code.split("-"))

        # Kiểm tra tính hợp lệ của r và s
        if r < 1 or r >= p or s < 0 or s >= p - 1:
            return False

        # Xác minh: y^r * r^s mod p == g^hash_code mod p
        left = (pow(y, r, p) * pow(r, s, p)) % p
        right = pow(g, hash_code, p)

        return left == right
    except:
        return None