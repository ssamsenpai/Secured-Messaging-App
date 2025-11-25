# crypto.py
# Simple Caesar cipher implementation, handles upper/lower letters.
from typing import Tuple
import random

# Task 1: Caesar Breaker
def load_words():
    try:
        with open('english_words.txt', 'r') as f:
            return set(word.strip().lower() for word in f)
    except FileNotFoundError:
        return set()

COMMON_WORDS = load_words()

def caesar_break(ciphertext: str, language: str = 'english') -> Tuple[str, int]:
    """
    Brute-force Caesar cipher and return the most likely plaintext and the key used.
    """
    # We ignore the language parameter as requested and focus on English
    vocab = COMMON_WORDS
    best_score = -1
    best_text = ""
    best_key = 0

    for key in range(26):
        # Decrypt with this key
        candidate = caesar_decrypt(ciphertext, key)
        
        # Score candidate
        words = candidate.split()
        score = 0
        for word in words:
            # clean word
            clean_word = ''.join(c for c in word if c.isalpha()).lower()
            if clean_word in vocab:
                score += 1
        
        if score > best_score:
            best_score = score
            best_text = candidate
            best_key = key
            
    return best_text, best_key

# Task 2: RSA Implementation
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_gcd(b % a, a)
        return g, x - (b // a) * y, y

def mod_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return (x % m + m) % m

def is_prime(n, k=5):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    # Miller-Rabin test
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=128):
    while True:
        n = random.getrandbits(bits)
        if n % 2 == 0:
            n += 1
        if is_prime(n):
            return n

def generate_keypair(keysize=1024):
    # Step 1: Generate two distinct large prime numbers p and q
    p = generate_prime(keysize // 2)
    q = generate_prime(keysize // 2)
    while p == q:
        q = generate_prime(keysize // 2)

    # Step 2: Compute n = p * q
    n = p * q
    
    # Step 3: Compute Euler's totient function phi(n) = (p - 1) * (q - 1)
    phi = (p - 1) * (q - 1)
    
    # Step 4: Choose an integer e such that 1 < e < phi(n) and gcd(e, phi(n)) = 1
    e = 65537
    while gcd(e, phi) != 1:
        p = generate_prime(keysize // 2)
        q = generate_prime(keysize // 2)
        while p == q:
            q = generate_prime(keysize // 2)
        n = p * q
        phi = (p - 1) * (q - 1)
        
    # Step 5: Determine d as d = e^(-1) mod phi(n)
    d = mod_inverse(e, phi)
    
    # Return Public Key (e, n) and Private Key (d, n)
    return ((e, n), (d, n))

def rsa_encrypt(plaintext: str, public_key) -> str:
    e, n = public_key
    # Convert string to int
    m = int.from_bytes(plaintext.encode('utf-8'), 'big')
    if m >= n:
        raise ValueError("Message too long for RSA key size")
    # Encryption formula: c = m^e mod n
    c = pow(m, e, n)
    return hex(c)[2:]

def rsa_decrypt(ciphertext: str, private_key) -> str:
    d, n = private_key
    try:
        c = int(ciphertext, 16)
        # Decryption formula: m = c^d mod n
        m = pow(c, d, n)
        num_bytes = (m.bit_length() + 7) // 8
        return m.to_bytes(num_bytes, 'big').decode('utf-8')
    except Exception as e:
        return f"[Error decrypting RSA: {e}]"

def caesar_encrypt(plaintext: str, key: int) -> str:
    result_chars = []
    for ch in plaintext:
        if 'a' <= ch <= 'z':
            base = ord('a')
            result_chars.append(chr((ord(ch) - base + key) % 26 + base))
        elif 'A' <= ch <= 'Z':
            base = ord('A')
            result_chars.append(chr((ord(ch) - base + key) % 26 + base))
        else:
            result_chars.append(ch)
    return ''.join(result_chars)

def caesar_decrypt(ciphertext: str, key: int) -> str:
    return caesar_encrypt(ciphertext, (-key) % 26)

def vigenere_encrypt(plaintext: str, key: str) -> str:
    result = []
    key = key.upper()
    key_index = 0

    for ch in plaintext:
        if ch.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
            key_index += 1
        else:
            result.append(ch)
    return ''.join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    result = []
    key = key.upper()
    key_index = 0

    for ch in ciphertext:
        if ch.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base - shift) % 26 + base))
            key_index += 1
        else:
            result.append(ch)
    return ''.join(result)


# Substitution cipher (monoalphabetic substitution)
def substitution_encrypt(plaintext: str, key: str) -> str:
    # key: 26-letter mapping representing ciphertext letters for A..Z
    clean_key = ''.join([c for c in key if c.isalpha()])
    if len(clean_key) != 26:
        raise ValueError("Substitution key must contain 26 letters")
    clean_key = clean_key.upper()
    mapping_upper = {chr(ord('A') + i): clean_key[i] for i in range(26)}
    mapping_lower = {k.lower(): v.lower() for k, v in mapping_upper.items()}

    result = []
    for ch in plaintext:
        if ch.isupper():
            result.append(mapping_upper.get(ch, ch))
        elif ch.islower():
            result.append(mapping_lower.get(ch, ch))
        else:
            result.append(ch)
    return ''.join(result)


def substitution_decrypt(ciphertext: str, key: str) -> str:
    clean_key = ''.join([c for c in key if c.isalpha()])
    if len(clean_key) != 26:
        raise ValueError("Substitution key must contain 26 letters")
    clean_key = clean_key.upper()
    mapping_upper = {clean_key[i]: chr(ord('A') + i) for i in range(26)}
    mapping_lower = {k.lower(): v.lower() for k, v in mapping_upper.items()}

    result = []
    for ch in ciphertext:
        if ch.isupper():
            result.append(mapping_upper.get(ch, ch))
        elif ch.islower():
            result.append(mapping_lower.get(ch, ch))
        else:
            result.append(ch)
    return ''.join(result)


# Simple columnar transposition cipher
# key: number of columns (int > 0). Encryption writes plaintext into rows
# left-to-right with that many columns and reads out column-by-column.
def transposition_encrypt(plaintext: str, key: int) -> str:
    cols = int(key)
    if cols <= 0:
        raise ValueError("Transposition key must be a positive integer")
    # keep all characters (including spaces and punctuation)
    # fill into rows
    rows = (len(plaintext) + cols - 1) // cols
    padded_len = rows * cols
    pad_char = 'X'
    padded = plaintext.ljust(padded_len, pad_char)

    result = []
    for c in range(cols):
        for r in range(rows):
            idx = r * cols + c
            result.append(padded[idx])
    return ''.join(result)


def transposition_decrypt(ciphertext: str, key: int) -> str:
    cols = int(key)
    if cols <= 0:
        raise ValueError("Transposition key must be a positive integer")
    length = len(ciphertext)
    rows = (length + cols - 1) // cols
    # build empty grid
    grid = [[''] * cols for _ in range(rows)]
    idx = 0
    for c in range(cols):
        for r in range(rows):
            if idx < length:
                grid[r][c] = ciphertext[idx]
                idx += 1

    # read row-wise
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(grid[r][c])

    # strip potential padding X characters added during encryption
    return ''.join(result).rstrip('X')


# A generic interface for later adding more ciphers
def encrypt(text: str, key, method: str = "caesar") -> str:
    if method == "caesar" or method == "caesar_break":
        return caesar_encrypt(text, int(key) % 26)
    elif method == "vigenere":
        return vigenere_encrypt(text, str(key))
    elif method == "substitution":
        return substitution_encrypt(text, str(key))
    elif method == "transposition":
        return transposition_encrypt(text, int(key))
    elif method == "rsa":
        return rsa_encrypt(text, key)
    else:
        raise ValueError("Unknown method")


def decrypt(text: str, key, method: str = "caesar") -> str:
    if method == "caesar":
        return caesar_decrypt(text, int(key) % 26)
    elif method == "caesar_break":
        # key here is the language string (ignored now)
        plaintext, found_key = caesar_break(text, str(key))
        return f"{plaintext} (shift {found_key})"
    elif method == "vigenere":
        return vigenere_decrypt(text, str(key))
    elif method == "substitution":
        return substitution_decrypt(text, str(key))
    elif method == "transposition":
        return transposition_decrypt(text, int(key))
    elif method == "rsa":
        return rsa_decrypt(text, key)
    else:
        raise ValueError("Unknown method")


# quick test
if __name__ == "__main__":
    print("[Caesar]", encrypt("Hello", 3), "→", decrypt(encrypt("Hello", 3), 3))
    print("[Vigenere]", encrypt("ATTACKATDAWN", "LEMON"), "→", decrypt(encrypt("ATTACKATDAWN", "LEMON"), "LEMON"))