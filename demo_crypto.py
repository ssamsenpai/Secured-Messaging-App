# demo_crypto.py
from crypto import substitution_encrypt, substitution_decrypt, transposition_encrypt, transposition_decrypt

def demo_substitution():
    plaintext = "Hello, World! 123"
    # example substitution key (26 letters): A->Q, B->W, C->E, ...
    key = "QWERTYUIOPASDFGHJKLZXCVBNM"
    print("--- Substitution Cipher Demo ---")
    print("Key:", key)
    ct = substitution_encrypt(plaintext, key)
    print("Plaintext:", plaintext)
    print("Ciphertext:", ct)
    pt = substitution_decrypt(ct, key)
    print("Decrypted:", pt)
    print()


def demo_transposition():
    plaintext = "Attack at dawn!"
    key = 4  # number of columns
    print("--- Transposition Cipher Demo ---")
    print("Key (columns):", key)
    ct = transposition_encrypt(plaintext, key)
    print("Plaintext:", plaintext)
    print("Ciphertext:", ct)
    pt = transposition_decrypt(ct, key)
    print("Decrypted:", pt)
    print()

if __name__ == '__main__':
    demo_substitution()
    demo_transposition()
