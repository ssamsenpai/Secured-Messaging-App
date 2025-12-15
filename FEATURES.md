# 🎨 Streamlit App Features Overview

## 📱 User Interface Components

### 1. Login/Registration Page
```
┌──────────────────────────────────────────────────┐
│         🔐 Secured Messenger App                 │
│         Authentication Required                   │
│                                                   │
│  ┌─────────────┬─────────────┐                  │
│  │   Login     │   Register   │                  │
│  ├─────────────┴──────────────┤                  │
│  │  Username: [_____________] │                  │
│  │  Password: [_____________] │                  │
│  │                            │                  │
│  │       [  Login  ]          │                  │
│  └────────────────────────────┘                  │
└──────────────────────────────────────────────────┘
```

**Features**:
- Two tabs: Login and Register
- Username/password input fields
- Password validation (min 6 characters)
- Password confirmation for registration
- Success/error messages
- Secure bcrypt hashing

---

### 2. Main Chat Interface

```
┌──────────────────────────────────────────────────┐
│  💬 Secured Messenger - Welcome, Alice!          │
├──────────────────────────────────────────────────┤
│                                                   │
│  [🔌 Connect to Chat]  Status: 🔴 Disconnected  │
│                                                   │
├──────────────────────────────────────────────────┤
│                Chat Messages                      │
│  ┌────────────────────────────────────────────┐ │
│  │ ℹ️ System: Connected as Alice              │ │
│  │                                            │ │
│  │ 👤 You: Hello!                             │ │
│  │   🔒 View Ciphertext ▼                     │ │
│  │                                            │ │
│  │ 🤖 Partner: Hi there!                      │ │
│  │   🔒 View Ciphertext ▼                     │ │
│  └────────────────────────────────────────────┘ │
│                                                   │
│  Type your message: [_______________________]   │
│                     [📤 Send Message]            │
└──────────────────────────────────────────────────┘
```

**Features**:
- Connection status indicator
- Real-time message display
- Sender identification (You/Partner/System)
- Expandable ciphertext view
- Message input form
- Auto-refresh for new messages

---

### 3. Sidebar - Encryption Settings

```
┌─────────────────────────────┐
│  🔐 Encryption Settings     │
├─────────────────────────────┤
│  Cipher Method:             │
│  [▼ Caesar Cipher        ]  │
│     • Caesar               │
│     • Vigenere            │
│     • Substitution        │
│     • Transposition       │
│     • RSA                 │
│     • Caesar Breaker      │
│                            │
│ ─────────────────────────  │
│                            │
│  Caesar Key (0-25): [3]    │
│                            │
└─────────────────────────────┘
```

**Dynamic Key Input** based on method:
- **Caesar**: Number input (0-25)
- **Vigenère**: Text input (keyword)
- **Substitution**: Text input (26 letters)
- **Transposition**: Number input (columns)
- **RSA**: "Generate Keypair" button + key display
- **Caesar Break**: Number for sending + auto-decrypt

---

### 4. Sidebar - Server Control

```
┌─────────────────────────────┐
│  🖥️ Server Control          │
├─────────────────────────────┤
│  Status: 🟢 Running         │
│                            │
│  [▶️ Start]  [⏹️ Stop]      │
│                            │
│ ─────────────────────────── │
│                            │
│  [🚪 Logout]                │
└─────────────────────────────┘
```

**Features**:
- Real-time status indicator
- Start button (disabled when running)
- Stop button (disabled when stopped)
- Logout button (cleans up connections)

---

## 🎬 User Flow Examples

### Example 1: New User Registration
1. Open `http://localhost:8501`
2. Click "Register" tab
3. Enter username: "alice"
4. Enter password: "secure123"
5. Confirm password: "secure123"
6. Click "Register" button
7. See success message
8. Switch to "Login" tab
9. Enter credentials
10. Click "Login"
11. Redirected to chat interface

### Example 2: Starting a Chat Session
1. Login as Alice
2. Click "▶️ Start" in Server Control
3. Wait for "🟢 Running" status
4. Select "Caesar Cipher" from dropdown
5. Set key to 5
6. Click "🔌 Connect to Chat"
7. Wait for "🟢 Connected" status
8. Type message: "Hello Bob!"
9. Click "📤 Send Message"
10. See encrypted message sent

### Example 3: Two Users Chatting
**Alice's Screen**:
```
👤 You: Hello Bob!
   🔒 Ciphertext: Mjqqt Gtg!
   
🤖 Partner: Hi Alice!
   🔒 Ciphertext: Mn Fqnhj!
```

**Bob's Screen**:
```
🤖 Partner: Hello Bob!
   🔒 Ciphertext: Mjqqt Gtg!
   
👤 You: Hi Alice!
   🔒 Ciphertext: Mn Fqnhj!
```

---

## 🔄 Real-time Features

### Auto-Refresh Mechanism
- Messages update automatically when connected
- No manual refresh needed
- 0.5 second polling interval
- Smooth message appearance

### Thread-Based Receiving
- Background thread listens for messages
- Non-blocking UI
- Graceful connection handling
- Error recovery

---

## 🎨 Visual Indicators

| Symbol | Meaning |
|--------|---------|
| 🟢 | Connected/Running |
| 🔴 | Disconnected/Stopped |
| 🔐 | Encryption-related |
| 🔌 | Connection action |
| 📤 | Send message |
| 🔒 | Ciphertext available |
| ℹ️ | System message |
| 👤 | Your message |
| 🤖 | Partner's message |
| 🖥️ | Server-related |
| 🚪 | Logout action |

---

## 📊 Message Display Format

### Your Messages
```
┌─────────────────────────────────────┐
│ 👤 You                              │
│ Hello World!                        │
│                                     │
│ 🔒 View Ciphertext ▼                │
│    Khoor Zruog!                     │
└─────────────────────────────────────┘
```

### Partner's Messages
```
┌─────────────────────────────────────┐
│ 🤖 Partner                          │
│ How are you?                        │
│                                     │
│ 🔒 View Ciphertext ▼                │
│    Krz duh brx?                     │
└─────────────────────────────────────┘
```

### System Messages
```
┌─────────────────────────────────────┐
│ ℹ️ Connected as Alice               │
└─────────────────────────────────────┘
```

---

## 🎯 Interactive Elements

### Buttons
- **Connect to Chat**: Establishes socket connection
- **Disconnect**: Closes socket connection
- **Start Server**: Launches server.py subprocess
- **Stop Server**: Terminates server process
- **Send Message**: Encrypts and sends message
- **Logout**: Cleans up and returns to login
- **Generate Keypair**: Creates new RSA keys

### Dropdowns
- **Cipher Method**: Select encryption algorithm

### Input Fields
- **Username**: Text input for authentication
- **Password**: Hidden text input
- **Caesar Key**: Number input with range
- **Vigenere Key**: Text input for keyword
- **Substitution Key**: Text input (26 chars)
- **Transposition Key**: Number input
- **Message**: Text input for chat

### Expandable Sections
- **View Ciphertext**: Shows encrypted version of message

---

## 🚀 Performance Features

### Optimizations
- Lazy loading of cipher keys
- Efficient message storage (session state)
- Background threading for I/O
- Graceful degradation on errors

### Resource Management
- Automatic socket cleanup
- Thread daemon mode
- Process termination on logout
- Memory-efficient message history

---

**The interface is designed to be intuitive, responsive, and educational - showing both plaintext and ciphertext to understand the encryption process!**
