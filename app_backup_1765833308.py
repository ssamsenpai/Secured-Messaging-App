# app.py
# Streamlit frontend for Secured Messenger App - Redesigned with #00C896
import streamlit as st
import socket
import threading
import time
import subprocess
import os
import hashlib
import json
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image
from crypto import encrypt, decrypt, generate_keypair
from auth import register_user, login_user, load_users

# Configuration
HOST = '127.0.0.1'
PORT = 65432

# Avatar colors and icons for users
AVATAR_COLORS = ['#00C896', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#6C5CE7', '#A29BFE']
AVATAR_ICONS = ['O', 'A', 'H', 'M', 'J', 'K', 'L', 'S']

def get_user_avatar(username):
    """Generate consistent avatar for user"""
    hash_val = int(hashlib.md5(username.encode()).hexdigest(), 16)
    color = AVATAR_COLORS[hash_val % len(AVATAR_COLORS)]
    # Use first letter of username
    icon = username[0].upper() if username else 'U'
    return color, icon

def save_face_image(username, image_data):
    """Save face image for user"""
    face_dir = "face_data"
    if not os.path.exists(face_dir):
        os.makedirs(face_dir)
    
    filepath = os.path.join(face_dir, f"{username}_face.jpg")
    
    if isinstance(image_data, Image.Image):
        image_data.save(filepath)
    else:
        with open(filepath, "wb") as f:
            f.write(image_data.read() if hasattr(image_data, 'read') else image_data)
    
    return True

def verify_face_image(username, new_image_data):
    """Verify face image matches stored image"""
    face_dir = "face_data"
    filepath = os.path.join(face_dir, f"{username}_face.jpg")
    
    if not os.path.exists(filepath):
        return False
    
    try:
        stored_img = Image.open(filepath)
        
        if isinstance(new_image_data, Image.Image):
            new_img = new_image_data
        else:
            new_img = Image.open(new_image_data)
        
        stored_img = stored_img.resize((200, 200))
        new_img = new_img.resize((200, 200))
        
        import numpy as np
        stored_array = np.array(stored_img)
        new_array = np.array(new_img)
        
        diff = np.abs(stored_array.astype(float) - new_array.astype(float))
        similarity = 1 - (diff.mean() / 255)
        
        return similarity > 0.6
    except Exception as e:
        print(f"Face verification error: {e}")
        return False

def has_face_data(username):
    """Check if user has face data stored"""
    face_dir = "face_data"
    filepath = os.path.join(face_dir, f"{username}_face.jpg")
    return os.path.exists(filepath)

def load_custom_css():
    """Load custom CSS matching the exact design with #00C896 theme"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        .stApp {
            background-color: #F5F5F5;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            min-width: 215px !important;
            width: 215px !important;
            max-width: 215px !important;
            border-right: 1px solid #E8E8E8 !important;
            padding: 0 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            bottom: 0 !important;
            z-index: 1000 !important;
        }
        
        section[data-testid="stSidebar"] > div {
            padding: 20px 0 !important;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Main Content */
        .main .block-container {
            margin-left: 215px !important;
            width: calc(100% - 215px) !important;
            padding: 0 !important;
            max-width: none !important;
            background-color: #F5F5F5;
            min-height: 100vh;
        }
        
        /* Header */
        .app-header {
            height: 64px;
            padding: 0 32px;
            background-color: #FFFFFF;
            border-bottom: 1px solid #E8E8E8;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
            font-weight: 600;
        }
        
        .header-name {
            font-size: 16px;
            font-weight: 600;
            color: #1A1A1A;
            margin-left: 12px;
        }
        
        /* Messages */
        .messages-area {
            padding: 24px 32px 110px 32px;
            background-color: #F5F5F5;
            min-height: calc(100vh - 64px);
        }
        
        .message-container {
            margin-bottom: 16px;
        }
        
        .message-header {
            font-size: 12px;
            color: #9E9E9E;
            margin-bottom: 6px;
            font-weight: 500;
        }
        
        .message-bubble {
            display: inline-block;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
            max-width: 600px;
            background-color: #FFFFFF;
            color: #1A1A1A;
        }
        
        .message-outgoing {
            text-align: right;
        }
        
        .message-outgoing .message-bubble {
            border-bottom-right-radius: 4px;
        }
        
        .message-incoming .message-bubble {
            border-bottom-left-radius: 4px;
        }
        
        .encrypted-text {
            font-size: 11px;
            color: #BDBDBD;
            margin-top: 4px;
        }
        
        /* Composer */
        .composer-container {
            position: fixed;
            bottom: 0;
            left: 215px;
            right: 0;
            background-color: #FFFFFF;
            border-top: 1px solid #E8E8E8;
            padding: 16px 32px;
            z-index: 950;
        }
        
        .composer-inner {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .composer-inner .stSelectbox > div > div,
        .composer-inner .stNumberInput > div {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            height: 44px;
        }
        
        .composer-inner .stTextInput input {
            height: 44px;
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 16px;
            color: #1A1A1A;
            font-size: 14px;
        }
        
        .composer-inner .stTextInput input::placeholder {
            color: #BDBDBD;
        }
        
        .composer-inner .stTextInput input:focus {
            border-color: #00C896;
            background-color: #FFFFFF;
            outline: none;
        }
        
        /* Send Button */
        .send-btn button {
            width: 48px !important;
            height: 48px !important;
            min-width: 48px !important;
            border-radius: 50% !important;
            background-color: #00C896 !important;
            color: white !important;
            padding: 0 !important;
            border: none !important;
            font-size: 20px !important;
        }
        
        .send-btn button:hover {
            background-color: #00B385 !important;
        }
        
        /* Logo */
        .sidebar-logo-container {
            padding: 0 16px 24px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .sidebar-logo-img {
            width: 32px;
            height: 32px;
            border-radius: 8px;
        }
        
        .sidebar-logo-text {
            font-size: 20px;
            font-weight: 700;
            color: #1A1A1A;
        }
        
        /* Friends */
        .sidebar-section-title {
            font-size: 11px;
            font-weight: 600;
            color: #9E9E9E;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 12px;
            padding: 0 16px;
        }
        
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            background-color: transparent !important;
            border: none !important;
            border-left: 3px solid transparent !important;
            color: #1A1A1A !important;
            text-align: left !important;
            padding: 12px 16px !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            transition: all 0.15s !important;
            justify-content: flex-start !important;
        }
        
        section[data-testid="stSidebar"] .stButton button:hover {
            background-color: #F5F5F5 !important;
        }
        
        section[data-testid="stSidebar"] .friend-item-active button {
            background-color: #E0F7F1 !important;
            border-left: 3px solid #00C896 !important;
        }
        
        /* Logout */
        .logout-container {
            margin-top: auto;
            padding: 16px;
            border-top: 1px solid #E8E8E8;
        }
        
        .logout-btn button {
            color: #9E9E9E !important;
            font-size: 13px !important;
            padding: 8px 0 !important;
        }
        
        #MainMenu, footer, header, .stDeployButton, [data-testid="stStatusWidget"] {
            display: none !important;
        }
        
        .stSelectbox, .stNumberInput, .stTextInput {
            margin-bottom: 0 !important;
        }
        
        ::-webkit-scrollbar {
            width: 6px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #E0E0E0;
            border-radius: 3px;
        }
        </style>
    """, unsafe_allow_html=True)

# [Rest of the code continues with session state initialization and functions...]
# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'socket' not in st.session_state:
    st.session_state.socket = None
if 'crypto_method' not in st.session_state:
    st.session_state.crypto_method = "caesar"
if 'crypto_key' not in st.session_state:
    st.session_state.crypto_key = 3
if 'decryption_key' not in st.session_state:
    st.session_state.decryption_key = None
if 'server_process' not in st.session_state:
    st.session_state.server_process = None
if 'server_running' not in st.session_state:
    st.session_state.server_running = False
if 'receiver_thread' not in st.session_state:
    st.session_state.receiver_thread = None
if 'active_chat' not in st.session_state:
    st.session_state.active_chat = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'show_reset_password' not in st.session_state:
    st.session_state.show_reset_password = False
if 'default_chat_set' not in st.session_state:
    st.session_state.default_chat_set = False

def receiver_loop(sock):
    """Background thread to receive messages"""
    while st.session_state.connected:
        try:
            data = sock.recv(4096)
            if not data:
                st.session_state.connected = False
                st.session_state.messages.append({"sender": "System", "text": "Server closed connection", "is_encrypted": False})
                break
            
            received_data = data.decode('utf-8', errors='ignore')
            
            if '|' in received_data:
                sender, ciphertext = received_data.split('|', 1)
            else:
                sender = st.session_state.active_chat if st.session_state.active_chat else "Partner"
                ciphertext = received_data
            
            try:
                d_key = st.session_state.decryption_key if st.session_state.decryption_key is not None else st.session_state.crypto_key
                plaintext = decrypt(ciphertext, d_key, st.session_state.crypto_method)
                
                st.session_state.messages.append({
                    "sender": sender,
                    "text": plaintext,
                    "ciphertext": ciphertext,
                    "is_encrypted": True,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
            except Exception as e:
                pass
        except Exception as e:
            if st.session_state.connected:
                st.session_state.messages.append({"sender": "System", "text": f"Connection error: {e}", "is_encrypted": False})
            st.session_state.connected = False
            break

def connect_to_server():
    """Connect to the chat server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        
        sock.sendall(st.session_state.username.encode('utf-8'))
        
        st.session_state.socket = sock
        st.session_state.connected = True
        
        thread = threading.Thread(target=receiver_loop, args=(sock,), daemon=True)
        thread.start()
        st.session_state.receiver_thread = thread
        return True
    except Exception as e:
        return False

def disconnect_from_server():
    """Disconnect from the chat server"""
    st.session_state.connected = False
    if st.session_state.socket:
        try:
            st.session_state.socket.close()
        except:
            pass
        st.session_state.socket = None

def send_message(message):
    """Encrypt and send a message"""
    if not st.session_state.connected or not st.session_state.socket:
        return False
    
    try:
        ciphertext = encrypt(message, st.session_state.crypto_key, st.session_state.crypto_method)
        message_with_sender = f"{st.session_state.username}|{ciphertext}"
        st.session_state.socket.sendall(message_with_sender.encode('utf-8'))
        
        st.session_state.messages.append({
            "sender": st.session_state.username,
            "text": message,
            "ciphertext": ciphertext,
            "is_encrypted": True,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        return True
    except Exception as e:
        return False

def start_server():
    """Start the server in a subprocess"""
    try:
        process = subprocess.Popen(['python', 'server.py'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   cwd=os.getcwd())
        st.session_state.server_process = process
        st.session_state.server_running = True
        time.sleep(1)
        return True
    except Exception as e:
        return False

def stop_server():
    """Stop the server subprocess"""
    if st.session_state.server_process:
        try:
            st.session_state.server_process.terminate()
            st.session_state.server_process.wait(timeout=3)
        except:
            st.session_state.server_process.kill()
        st.session_state.server_process = None
    st.session_state.server_running = False

def login_page():
    """Display login/registration page"""
    load_custom_css()
    
    st.markdown("<h1 style='text-align: center; color: #00C896; margin-top: 60px;'>🔐 MSecure</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #9E9E9E; margin-bottom: 40px;'>Secure Messaging Platform</h3>", unsafe_allow_html=True)
    
    if st.session_state.show_reset_password:
        st.subheader("Reset Password with Face Verification")
        
        reset_username = st.text_input("Username", key="reset_username")
        
        if has_face_data(reset_username):
            st.info("📸 Please capture your face to verify your identity")
            
            face_image = st.camera_input("Take a photo", key="reset_face")
            
            if face_image:
                if verify_face_image(reset_username, face_image):
                    st.success("✅ Face verified! You can now reset your password")
                    
                    new_password = st.text_input("New Password", type="password", key="new_pass")
                    confirm_new = st.text_input("Confirm New Password", type="password", key="confirm_new")
                    
                    if st.button("Reset Password", use_container_width=True):
                        if new_password == confirm_new and len(new_password) >= 6:
                            from auth import hash_password, save_users
                            users = load_users()
                            users[reset_username] = hash_password(new_password)
                            save_users(users)
                            
                            st.success("Password reset successful! Redirecting to login...")
                            st.session_state.show_reset_password = False
                            st.session_state.login_attempts = 0
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Passwords must match and be at least 6 characters")
                else:
                    st.error("❌ Face verification failed. Please try again.")
        else:
            st.error("No face data found for this user. Cannot reset password.")
        
        if st.button("Back to Login", type="secondary", use_container_width=True):
            st.session_state.show_reset_password = False
            st.session_state.login_attempts = 0
            st.rerun()
    
    else:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                success, message = login_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error(message)
                    
                    if st.session_state.login_attempts >= 2:
                        if has_face_data(username):
                            st.warning("Too many failed attempts. Redirecting to password reset...")
                            time.sleep(2)
                            st.session_state.show_reset_password = True
                            st.rerun()
        
        with tab2:
            st.info("🔐 Your face image will be securely stored locally for password recovery only.")
            
            new_username = st.text_input("Username", key="reg_username")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            face_image = st.camera_input("Take a photo for Face ID", key="reg_face")
            
            consent = st.checkbox("I consent to storing my face image for password recovery")
            
            if st.button("Register", use_container_width=True):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not face_image:
                    st.error("Please capture your face for registration")
                elif not consent:
                    st.error("Please consent to storing your face image")
                else:
                    success, message = register_user(new_username, new_password)
                    if success:
                        save_face_image(new_username, face_image)
                        st.success(message + " - You can now login")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        # Logo
        st.markdown("""
            <div class="sidebar-logo-container">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%2300C896'/%3E%3Cpath d='M50 30 L50 50 M30 50 L70 50' stroke='white' stroke-width='8' stroke-linecap='round'/%3E%3Cpath d='M35 60 Q50 70 65 60' stroke='white' stroke-width='6' stroke-linecap='round' fill='none'/%3E%3Ccircle cx='40' cy='35' r='4' fill='white'/%3E%3Ccircle cx='60' cy='35' r='4' fill='white'/%3E%3C/svg%3E" class="sidebar-logo-img" alt="Logo"/>
                <span class="sidebar-logo-text">MSecure</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-title">Friends</div>', unsafe_allow_html=True)
        
        all_users = load_users()
        available_users = [user for user in all_users.keys() if user != st.session_state.username]
        
        if not st.session_state.default_chat_set and available_users:
            st.session_state.active_chat = available_users[0]
            st.session_state.default_chat_set = True
            if not st.session_state.connected:
                connect_to_server()
        
        for user in available_users:
            color, icon = get_user_avatar(user)
            is_active = (user == st.session_state.active_chat)
            
            if is_active:
                st.markdown('<div class="friend-item-active">', unsafe_allow_html=True)
            
            if st.button(f"{icon}  {user}", key=f"user_{user}", use_container_width=True):
                st.session_state.active_chat = user
                if not st.session_state.connected:
                    connect_to_server()
                st.rerun()
            
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="logout-container"><div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            if st.session_state.connected:
                disconnect_from_server()
            if st.session_state.server_running:
                stop_server()
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.active_chat = None
            st.session_state.default_chat_set = False
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

def render_header():
    """Render header"""
    recipient_name = st.session_state.active_chat if st.session_state.active_chat else "Select a friend"
    
    if st.session_state.active_chat:
        color, icon = get_user_avatar(st.session_state.active_chat)
    else:
        color, icon = "#00C896", "O"
    
    status_text = "Running" if st.session_state.server_running else "Stopped"
    
    col1, col2, col3, col4 = st.columns([0.5, 2, 8, 2])
    
    with col1:
        st.markdown(f'<div class="header-avatar" style="background-color: {color};">{icon}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="header-name">{recipient_name}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<span style="font-size: 14px; color: #1A1A1A;">Server</span>', unsafe_allow_html=True)
    with col4:
        server_toggle = st.toggle("", value=st.session_state.server_running, key="server_toggle", label_visibility="collapsed")
        if server_toggle != st.session_state.server_running:
            if server_toggle:
                start_server()
            else:
                stop_server()
            st.session_state.server_running = server_toggle
            st.rerun()
        
        st.markdown(f'<span style="font-size: 13px; color: #{"00C896" if st.session_state.server_running else "FF5252"}; margin-left: 8px;">{status_text}</span>', unsafe_allow_html=True)

def render_messages():
    """Render messages"""
    st.markdown('<div class="messages-area">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown('<div style="text-align: center; color: #BDBDBD; padding: 40px;">No messages yet. Start chatting!</div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            sender = msg["sender"]
            is_user = (sender == st.session_state.username)
            timestamp = msg.get("timestamp", datetime.now().strftime("%I:%M %p"))
            
            msg_class = "message-outgoing" if is_user else "message-incoming"
            sender_label = "You" if is_user else sender
            
            encrypted_info = f'<div class="encrypted-text">🔒 Encrypted: {msg.get("ciphertext", "")[:30]}...</div>' if msg.get("is_encrypted") else ''
            
            st.markdown(f"""
                <div class="message-container {msg_class}">
                    <div class="message-header">{timestamp} {sender_label}</div>
                    <div class="message-bubble">{msg['text']}</div>
                    {encrypted_info}
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_message_input():
    """Render composer"""
    if not st.session_state.active_chat:
        return
    
    if not st.session_state.connected:
        st.markdown('<div class="composer-container"><div class="composer-inner">', unsafe_allow_html=True)
        if st.button("Connect to Chat", use_container_width=True):
            if connect_to_server():
                st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="composer-container"><div class="composer-inner">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1.2, 1, 6, 0.6])
    
    with col1:
        method = st.selectbox(
            "Cipher",
            ["caesar", "vigenere", "substitution", "transposition", "rsa", "caesar_break"],
            index=["caesar", "vigenere", "substitution", "transposition", "rsa", "caesar_break"].index(st.session_state.crypto_method),
            label_visibility="collapsed",
            key="cipher_method"
        )
        
        if method != st.session_state.crypto_method:
            st.session_state.crypto_method = method
            st.session_state.decryption_key = None
    
    with col2:
        if method == "caesar":
            key = st.number_input("Key", min_value=0, max_value=25, value=3, label_visibility="collapsed")
            st.session_state.crypto_key = key
        elif method == "vigenere":
            key = st.text_input("Key", value="LEMON", label_visibility="collapsed", key="vig_key")
            st.session_state.crypto_key = key.upper()
        elif method == "substitution":
            key = st.text_input("Key", value="QWERTYUIOPASDFGHJKLZXCVBNM", max_chars=26, label_visibility="collapsed", key="sub_key")
            if len(key) == 26:
                st.session_state.crypto_key = key.upper()
        elif method == "transposition":
            key = st.number_input("Cols", min_value=1, value=5, label_visibility="collapsed", key="trans_key")
            st.session_state.crypto_key = int(key)
        elif method == "rsa":
            if st.button("Gen Keys", use_container_width=True):
                public_key, private_key = generate_keypair(1024)
                st.session_state.crypto_key = public_key
                st.session_state.decryption_key = private_key
        elif method == "caesar_break":
            key = st.number_input("Key", min_value=0, max_value=25, value=3, label_visibility="collapsed", key="break_key")
            st.session_state.crypto_key = key
            st.session_state.decryption_key = "english"
    
    with col3:
        message = st.text_input(
            "Message",
            key="message_input",
            placeholder="Write your message here..",
            label_visibility="collapsed"
        )
    
    with col4:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send_clicked = st.button("►", key="send_btn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if send_clicked and message and message.strip():
            if send_message(message):
                st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def chat_page():
    """Main chat interface"""
    load_custom_css()
    
    render_sidebar()
    
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    render_header()
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_messages()
    render_message_input()
    
    if st.session_state.connected:
        time.sleep(0.5)
        st.rerun()

def main():
    """Main app entry point"""
    st.set_page_config(
        page_title="MSecure - Secured Messenger",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if not st.session_state.authenticated:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
