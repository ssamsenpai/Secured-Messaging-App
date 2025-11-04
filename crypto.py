# crypto.py
# Simple Caesar cipher implementation, handles upper/lower letters.
from typing import Tuple

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
    if method == "caesar":
        return caesar_encrypt(text, int(key) % 26)
    elif method == "vigenere":
        return vigenere_encrypt(text, str(key))
    elif method == "substitution":
        return substitution_encrypt(text, str(key))
    elif method == "transposition":
        return transposition_encrypt(text, int(key))
    else:
        raise ValueError("Unknown method")


def decrypt(text: str, key, method: str = "caesar") -> str:
    if method == "caesar":
        return caesar_decrypt(text, int(key) % 26)
    elif method == "vigenere":
        return vigenere_decrypt(text, str(key))
    elif method == "substitution":
        return substitution_decrypt(text, str(key))
    elif method == "transposition":
        return transposition_decrypt(text, int(key))
    else:
        raise ValueError("Unknown method")


# quick test
if __name__ == "__main__":
    print("[Caesar]", encrypt("Hello", 3), "→", decrypt(encrypt("Hello", 3), 3))
    print("[Vigenere]", encrypt("ATTACKATDAWN", "LEMON"), "→", decrypt(encrypt("ATTACKATDAWN", "LEMON"), "LEMON"))