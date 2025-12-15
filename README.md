🔐 Secure Messaging App

A Python-based client–server messaging application with a modern Streamlit frontend.
It focuses on encryption, hashing, and secure authentication while providing an intuitive chat interface.

⸻

🎯 Project Objective

This project demonstrates:
	•	Secure chat system using socket programming (TCP)
	•	End-to-end encryption (clients encrypt/decrypt, server only forwards ciphertext)
	•	Multiple cryptographic methods:
		•	Caesar Cipher
		•	Vigenère Cipher
		•	Substitution Cipher
		•	Transposition Cipher
		•	RSA (Public-key cryptography)
		•	Caesar Auto-Breaker
	•	Secure user authentication with bcrypt password hashing
	•	Modern web-based UI with Streamlit

⸻

🧠 Features
	•	✔️ **Streamlit Web Interface** - Modern, user-friendly chat UI
	•	✔️ **User Authentication** - Secure login/registration with bcrypt password hashing
	•	✔️ **Multiple Cipher Methods** - Switch between 6 different encryption methods in real-time
	•	✔️ **Server Control** - Start/stop server directly from the UI
	•	✔️ **End-to-End Encryption** - Messages encrypted on client side, server never sees plaintext
	•	✔️ **Multi-Client Support** - Multiple users can chat simultaneously
	•	✔️ **Real-time Messaging** - Live message updates with encryption/decryption

⸻

📁 Project Structure

messenger_project/
├── app.py               # Streamlit frontend application
├── auth.py              # Authentication system with bcrypt
├── client.py            # CLI client (legacy)
├── server.py            # Server that broadcasts encrypted messages
├── crypto.py            # All cipher implementations
├── users.json           # User database (auto-generated)
├── english_words.txt    # Dictionary for Caesar breaker
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

⸻

🚀 How to Run the Application

### Option 1: Streamlit Web Interface (Recommended)

1. Install dependencies

pip install -r requirements.txt

2. Run the Streamlit app

streamlit run app.py

3. Open your browser at http://localhost:8501

4. Create an account or login

5. Start the server using the sidebar button

6. Connect to chat and start messaging!

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
