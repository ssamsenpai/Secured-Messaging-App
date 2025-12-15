# Quick Start Guide - Secured Messenger App

## 🚀 Getting Started in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Launch the App
```bash
streamlit run app.py
```

### Step 3: Use the Application

1. **Register an Account**
   - Click the "Register" tab
   - Choose a username and password (min 6 characters)
   - Password is securely hashed with bcrypt ✅

2. **Login**
   - Enter your credentials
   - Click "Login"

3. **Start the Server**
   - Look at the left sidebar
   - Click "▶️ Start" under Server Control
   - Wait for status to show "🟢 Running"

4. **Choose Your Encryption Method**
   - Select from dropdown in sidebar:
     - **Caesar**: Simple shift cipher (key: 0-25)
     - **Vigenère**: Keyword-based cipher
     - **Substitution**: 26-letter mapping
     - **Transposition**: Column-based rearrangement
     - **RSA**: Public-key encryption (click "Generate Keypair")
     - **Caesar Break**: Auto-decrypt incoming Caesar messages

5. **Connect to Chat**
   - Click "🔌 Connect to Chat" button
   - Wait for connection confirmation

6. **Start Messaging!**
   - Type your message in the input box
   - Click "📤 Send Message"
   - Messages are encrypted before sending
   - Received messages are automatically decrypted
   - View ciphertext by expanding the 🔒 section

## 👥 Testing with Multiple Users

### Option 1: Multiple Browser Tabs
1. Open 2+ browser tabs to `http://localhost:8501`
2. Register different users in each tab
3. Start server from ONE tab only
4. Connect all users to chat
5. Send messages between tabs

### Option 2: Multiple Streamlit Instances
```bash
# Terminal 1 (User 1)
streamlit run app.py --server.port 8501

# Terminal 2 (User 2)
streamlit run app.py --server.port 8502

# Terminal 3 (User 3)
streamlit run app.py --server.port 8503
```

## 🔐 Encryption Examples

### Caesar Cipher
- **Key**: 3
- **Plaintext**: "Hello"
- **Ciphertext**: "Khoor"

### Vigenère Cipher
- **Key**: "LEMON"
- **Plaintext**: "ATTACKATDAWN"
- **Ciphertext**: "LXFOPVEFRNHR"

### RSA
- **Key**: Auto-generated (e, n) pair
- **Plaintext**: "Hello"
- **Ciphertext**: Long hexadecimal string

## 🛡️ Security Features

✅ **Password Hashing**: bcrypt with salt (never stores plain passwords)
✅ **End-to-End Encryption**: Server only sees ciphertext
✅ **Multiple Ciphers**: Choose your encryption method
✅ **Local Key Storage**: Keys never transmitted to server

## 🔧 Troubleshooting

**Problem**: "Connection failed"
- **Solution**: Make sure server is started first (click ▶️ Start)

**Problem**: "Address already in use"
- **Solution**: Stop the server (⏹️ Stop) and restart

**Problem**: Messages not decrypting correctly
- **Solution**: Make sure both users have the same cipher method and key

**Problem**: Can't login after registration
- **Solution**: Check that `users.json` file was created in project directory

## 📝 Tips

💡 **Share Keys Securely**: For Vigenère/Substitution, share the key with your chat partner outside the app

💡 **RSA Key Exchange**: In RSA mode, share your public key (e, n) with your partner

💡 **Caesar Breaker**: Automatically attempts to decrypt Caesar-encrypted messages without knowing the key

💡 **Server Logs**: Check terminal where server is running to see encrypted messages being forwarded

---

**Enjoy secure messaging! 🔐💬**
