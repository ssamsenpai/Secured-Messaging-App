# client.py
import socket
import threading
import json
from crypto import encrypt, decrypt

HOST = '127.0.0.1'
PORT = 65432

def receiver(sock, key, method):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("[*] Server closed connection")
                break
            ciphertext = data.decode('utf-8', errors='ignore')
            # Decrypt locally
            plaintext = decrypt(ciphertext, key, method)
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
    choice = input("Enter 1 or 2: ").strip()
    if choice == "2":
        method = "vigenere"
        key = input("Enter Vigenere key (word): ").strip().upper()
    else:
        # allow more methods
        if choice == "3":
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
            method = "caesar"
            while True:
                try:
                    key = int(input("Enter Caesar key (0-25): ").strip())
                    break
                except:
                    print("Enter an integer.")
    
    print(f"Using {method} with key={key}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # send nickname first (simple)
        s.sendall(nickname.encode('utf-8'))
        # start receiver thread
        t = threading.Thread(target=receiver, args=(s, key, method), daemon=True)
        t.start()

        try:
            while True:
                msg = input("> ")
                if msg.lower() == "/quit":
                    break
                if msg.strip() == "":
                    continue
                # Encrypt locally before sending
                ciphertext = encrypt(msg, key, method)
                s.sendall(ciphertext.encode('utf-8'))
                # Also show local clear text and ciphertext
                print(f"(sent ciphertext: {ciphertext})")
        except KeyboardInterrupt:
            print("\nExiting.")
        finally:
            s.close()

if __name__ == "__main__":
    main()