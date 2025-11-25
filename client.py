# client.py
import socket
import threading
import json
from crypto import encrypt, decrypt, generate_keypair

HOST = '127.0.0.1'
PORT = 65432

def receiver(sock, key, method, decryption_key=None):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("[*] Server closed connection")
                break
            ciphertext = data.decode('utf-8', errors='ignore')
            # Decrypt locally
            d_key = decryption_key if decryption_key is not None else key
            plaintext = decrypt(ciphertext, d_key, method)
            print(f"\n[RECV] (ciphertext: {ciphertext})\n[PLAINTEXT] {plaintext}\n> ", end='', flush=True)
        except Exception as e:
            print("Receive error:", e)
            break

def main():
    nickname = input("Choose your nickname: ").strip() or "anon"
    # choose cipher and key
    print("Choose cipher method:")
    print("1 - Caesar Cipher")
    print("2 - Vigenere Cipher")
    print("3 - Substitution Cipher")
    print("4 - Transposition Cipher")
    print("5 - RSA (Public Key)")
    print("6 - Caesar Auto-Breaker")
    choice = input("Enter choice: ").strip()
    
    decryption_key = None

    if choice == "6":
        method = "caesar_break"
        # Language is now defaulted to English/ignored as per request
        decryption_key = "english" 
        try:
            key = int(input("Enter key to use for SENDING (0-25): ").strip())
        except:
            key = 0

    elif choice == "5":
        method = "rsa"
        print("Generating RSA keypair (this may take a moment)...")
        public_key, private_key = generate_keypair(1024)
        print(f"Your Public Key: (e={public_key[0]}, n={public_key[1]})")
        print("Share this with your partner.")
        
        print("Enter partner's Public Key:")
        try:
            e_input = int(input("e: ").strip())
            n_input = int(input("n: ").strip())
            key = (e_input, n_input)
            decryption_key = private_key
        except:
            print("Invalid key format.")
            return

    elif choice == "2":
        method = "vigenere"
        key = input("Enter Vigenere key (word): ").strip().upper()
    elif choice == "3":
        method = "substitution"
        while True:
            key = input("Enter substitution key (26 letters, mapping for A..Z): ").strip()
            clean = ''.join([c for c in key if c.isalpha()])
            if len(clean) == 26:
                key = clean.upper()
                break
            print("Key must contain 26 letters (A-Z). Try again.")
    elif choice == "4":
        method = "transposition"
        while True:
            try:
                key = int(input("Enter transposition key (number of columns > 0): ").strip())
                if key > 0:
                    break
                print("Enter an integer > 0.")
            except:
                print("Enter an integer.")
    else:
        # Caesar
        method = "caesar"
        try:
            key = int(input("Enter Caesar key (0-25): ").strip())
        except:
            print("Enter an integer.")
            key = 0
    
    print(f"Using {method} with key={key}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # send nickname first (simple)
        s.sendall(nickname.encode('utf-8'))
        # start receiver thread
        t = threading.Thread(target=receiver, args=(s, key, method, decryption_key), daemon=True)
        t.start()

        try:
            while True:
                msg = input("> ")
                if msg.lower() == "/quit":
                    break
                if msg.strip() == "":
                    continue
                # Encrypt locally before sending
                try:
                    ciphertext = encrypt(msg, key, method)
                    s.sendall(ciphertext.encode('utf-8'))
                    # Also show local clear text and ciphertext
                    print(f"(sent ciphertext: {ciphertext})")
                except Exception as e:
                    print(f"Encryption error: {e}")
        except KeyboardInterrupt:
            print("\nExiting.")
        finally:
            s.close()

if __name__ == "__main__":
    main()