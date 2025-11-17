🔐 Secure Messaging App

A simple yet educational Python-based client–server messaging application built throughout the semester.
It focuses on learning and applying encryption, hashing, and authentication concepts while building a functional messaging system.

⸻

🎯 Project Objective

This project aims to:
	•	Build a secure chat system using socket programming (TCP).
	•	Ensure confidentiality by encrypting messages on the client side.
	•	Prevent the server from ever seeing plaintext messages.
	•	Implement classical cryptography techniques:
	•	Caesar Cipher
	•	Vigenère Cipher
	•	Prepare for advanced concepts such as hashing, salting, and user authentication.

⸻

🧠 Current Features (Week 2)
	•	✔️ Client–server architecture (Python sockets)
	•	✔️ Caesar cipher encryption & decryption
	•	✔️ Vigenère cipher encryption & decryption
	•	✔️ End-to-end encryption (clients encrypt/decrypt, server only forwards ciphertext)
	•	✔️ Multiple clients supported simultaneously

Server only logs encrypted messages, maintaining confidentiality.

⸻

📁 Project Structure

messenger_project/
├── client.py        # Client interface (console-based)
├── server.py        # Server that broadcasts encrypted messages
├── crypto.py        # Caesar & Vigenère cipher implementations
└── README.md        # Project documentation


⸻

🚀 How to Run the Application

1. Start the server

python server.py

2. Open two or more terminals and start clients

python client.py

3. Follow the on-screen steps
	•	Choose a nickname
	•	Select encryption method:
	•	1 → Caesar
	•	2 → Vigenère
	•	Enter the encryption key
	•	Start chatting securely 🎉

⸻

📡 Example Outputs

Server console

[Encrypted log] from Alice: LXFOPVEFRNHR

Client console

[RECV] (ciphertext: LXFOPVEFRNHR)
[PLAINTEXT] ATTACKATDAWN


⸻

🔒 Encryption Methods Overview

Cipher	Key Type	Description	Example
Caesar	Integer	Shifts each letter by a fixed number.	“HELLO” + 3 → “KHOOR”
Vigenère	Word	Each letter of key determines the shift amount.	“HELLO” + “KEY” → “RIJVS”

Message Flow:
	1.	User writes message
	2.	Client encrypts it
	3.	Server forwards ciphertext
	4.	Client decrypts it locally

⸻

📌 Next Steps (Planned)

Future improvements for upcoming sessions:
	•	🔑 Add user authentication (username + hashed password)
	•	💬 Store persistent chat history
	•	🎨 Build a modern UI (Lovable / graphical interface)
	•	🔐 Add more encryption & hashing:
	•	SHA-256 hashing
	•	Diffie–Hellman key exchange
	•	Simple RSA implementation (optional)
	•	👥 Multi-room chat support

⸻

🧬 About

Bioinformatics Student — USTHB
This project is developed as part of the BIO module, focusing on practical applications of cryptography and secure communication.
