# server.py
import socket
import threading
from crypto import caesar_break

HOST = '127.0.0.1'   # localhost for testing
PORT = 65432

clients = {}  # socket -> nickname

def broadcast(sender_sock, data: bytes):
    # forward ciphertext to all other clients (or implement targeted forwarding)
    for sock in list(clients.keys()):
        if sock is not sender_sock:
            try:
                sock.sendall(data)
            except:
                sock.close()
                del clients[sock]

def handle_client(conn, addr):
    print(f"[+] Connected {addr}")
    try:
        # first message: nickname (plaintext or encrypted? for simplicity, treat nickname as first message in plain)
        nickname = conn.recv(1024).decode('utf-8', errors='ignore').strip()
        if not nickname:
            nickname = str(addr)
        clients[conn] = nickname
        print(f"Client name: {nickname}")
        while True:
            data = conn.recv(4096)
            if not data:
                break
            # data is expected to be ciphertext bytes
            msg = data.decode('utf-8', errors='ignore')
            
            # Log ciphertext only:
            # If it looks like RSA (long hex string), print the integer value c (result of the formula)
            try:
                # RSA 1024 bits is ~256 hex chars. We use a threshold to distinguish from short text.
                if len(msg) > 32: 
                    c_val = int(msg, 16)
                    print(f"[Encrypted log] from {nickname}: c = {c_val}")
                else:
                    # Try to auto-break Caesar for logging purposes
                    try:
                        broken_text, shift = caesar_break(msg)
                        # Only show if it looks meaningful (shift != 0 or just show it anyway)
                        print(f"[Encrypted log] from {nickname}: {msg} -> {broken_text} (shift {shift})")
                    except:
                        print(f"[Encrypted log] from {nickname}: {msg}")
            except ValueError:
                # Not a hex string (e.g. Caesar text), print as is
                try:
                    broken_text, shift = caesar_break(msg)
                    print(f"[Encrypted log] from {nickname}: {msg} -> {broken_text} (shift {shift})")
                except:
                    print(f"[Encrypted log] from {nickname}: {msg}")

            # Forward ciphertext to other clients
            broadcast(conn, data)
    except Exception as e:
        print("Client error:", e)
    finally:
        print(f"[-] Disconnected {addr}")
        if conn in clients:
            del clients[conn]
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Allow reusing the address to avoid "Address already in use" errors
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    main()