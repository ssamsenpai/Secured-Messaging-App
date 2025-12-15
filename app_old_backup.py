# app.py
# Streamlit frontend for Secured Messenger App - Redesigned
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

# Avatar colors and icons for users - darker colors
AVATAR_COLORS = ['#C44569', '#2C3A47', '#218C74', '#E1B12C', '#6C5CE7', '#0984E3', '#D63031', '#00B894']
AVATAR_ICONS = ['👤', '🧑', '👨', '👩', '🧔', '👱', '🧑‍💼', '👨‍💻']

def get_user_avatar(username):
    """Generate consistent avatar for user"""
    hash_val = int(hashlib.md5(username.encode()).hexdigest(), 16)
    color = AVATAR_COLORS[hash_val % len(AVATAR_COLORS)]
    icon = AVATAR_ICONS[hash_val % len(AVATAR_ICONS)]
    return color, icon

def stIconMaterial(icon_name, color="#333", size="24px"):
    """Helper to render Material Icons"""
    return f'<i class="material-icons" style="color: {color}; font-size: {size}; vertical-align: middle;">{icon_name}</i>'

def save_face_image(username, image_data):
    """Save face image for user"""
    face_dir = "face_data"
    if not os.path.exists(face_dir):
        os.makedirs(face_dir)
    
    filepath = os.path.join(face_dir, f"{username}_face.jpg")
    
    # If image_data is PIL Image
    if isinstance(image_data, Image.Image):
        image_data.save(filepath)
    else:
        # If it's bytes or file-like object
        with open(filepath, "wb") as f:
            f.write(image_data.read() if hasattr(image_data, 'read') else image_data)
    
    return True

def verify_face_image(username, new_image_data):
    """Verify face image matches stored image (simple comparison)"""
    face_dir = "face_data"
    filepath = os.path.join(face_dir, f"{username}_face.jpg")
    
    if not os.path.exists(filepath):
        return False
    
    try:
        # Load stored image
        stored_img = Image.open(filepath)
        
        # Convert new image
        if isinstance(new_image_data, Image.Image):
            new_img = new_image_data
        else:
            new_img = Image.open(new_image_data)
        
        # Resize both to same size for comparison
        stored_img = stored_img.resize((200, 200))
        new_img = new_img.resize((200, 200))
        
        # Simple pixel-by-pixel comparison (basic verification)
        # In production, use proper face recognition library
        import numpy as np
        stored_array = np.array(stored_img)
        new_array = np.array(new_img)
        
        # Calculate similarity (simple method)
        diff = np.abs(stored_array.astype(float) - new_array.astype(float))
        similarity = 1 - (diff.mean() / 255)
        
        # If images are more than 60% similar, accept
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
    """Load custom CSS with Plus Jakarta Sans font and #2E45E0 theme"""
    st.markdown("""
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            box-sizing: border-box;
        }
        
        /* Global App Styling */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #F3F4F6 !important;
            min-width: 280px !important;
            width: 280px !important;
            max-width: 280px !important;
            border-right: none !important;
            padding-top: 16px !important;
            padding-left: 16px !important;
            padding-right: 16px !important;
            gap: 16px !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            bottom: 0 !important;
            z-index: 1000 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        /* Hide sidebar collapse button */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Main Content Area */
        .main .block-container {
            margin-left: 280px !important;
            width: calc(100% - 280px) !important;
            padding: 0 !important;
            max-width: none !important;
            background-color: #F5F6F8;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header Styling */
        .app-header {
            height: 56px;
            padding: 0 20px;
            background-color: #FFFFFF;
            border-bottom: 1px solid #E5E7EB;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: fixed;
            top: 0;
            left: 280px;
            right: 0;
            z-index: 900;
        }
        
        /* Messages Area */
        .messages-area {
            margin-top: 56px; /* Header height */
            padding: 20px;
            padding-bottom: 104px; /* Composer height (84) + 20 */
            background-color: #F5F6F8;
            min-height: calc(100vh - 56px);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        /* Composer Styling */
        .composer-container {
            position: fixed;
            bottom: 0;
            left: 280px;
            right: 0;
            height: 84px;
            background-color: #FFFFFF;
            border-top: 1px solid #E5E7EB;
            padding: 12px 20px;
            z-index: 950;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .composer-inner {
            width: 100%;
            max-width: 980px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* Sidebar Elements */
        .sidebar-logo-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding: 0 8px;
        }
        
        .sidebar-logo-text {
            font-size: 18px;
            font-weight: 700;
            color: #111827;
        }
        
        .sidebar-section-title {
            font-size: 12px;
            font-weight: 600;
            color: #6B7280;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
            padding: 0 8px;
        }
        
        /* Friend Item Button Styling */
        .stButton button {
            width: 100%;
            border: none;
            background-color: transparent;
            color: #111827;
            text-align: left;
            padding: 8px 10px;
            border-radius: 10px;
            height: 44px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        
        .stButton button:hover {
            background-color: #E5E7EB;
            color: #111827;
        }
        
        .stButton button:focus {
            box-shadow: 0 0 0 2px rgba(37,99,235,0.45);
        }
        
        /* Active Friend Item */
        .friend-item-active button {
            background-color: rgba(37,99,235,0.10) !important;
            color: #1D4ED8 !important;
        }
        
        /* Logout Button */
        .logout-container {
            margin-top: auto;
            padding-top: 16px;
        }
        
        .logout-btn button {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            justify-content: center;
            height: 40px;
        }
        
        .logout-btn button:hover {
            background-color: #F9FAFB !important;
        }
        
        /* Message Bubbles */
        .message-bubble {
            max-width: 520px;
            padding: 10px 12px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.5;
            box-shadow: 0 1px 2px rgba(0,0,0,0.06);
            position: relative;
        }
        
        .message-incoming {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            color: #111827;
            align-self: flex-start;
            border-top-left-radius: 4px;
        }
        
        .message-outgoing {
            background-color: rgba(37,99,235,0.10);
            border: 1px solid rgba(37,99,235,0.25);
            color: #1D4ED8;
            align-self: flex-end;
            border-top-right-radius: 4px;
        }
        
        .message-meta {
            font-size: 11px;
            color: #6B7280;
            margin-bottom: 4px;
            display: flex;
            gap: 8px;
        }
        
        .message-incoming-container {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .message-outgoing-container {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            margin-bottom: 12px;
        }
        
        /* Encrypted Chip */
        .encrypted-chip {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 8px 12px;
            max-width: 680px;
            margin: 0 auto 12px auto;
            box-shadow: 0 1px 2px rgba(0,0,0,0.06);
            font-size: 12px;
            color: #6B7280;
            text-align: center;
        }
        
        /* Composer Controls */
        .composer-control {
            height: 44px;
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 0 12px;
            display: flex;
            align-items: center;
        }
        
        /* Streamlit Input Overrides for Composer */
        .composer-inner .stTextInput input {
            height: 44px;
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 0 14px;
            color: #111827;
        }
        
        .composer-inner .stTextInput input:focus {
            border-color: #2563EB;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.45);
        }
        
        .composer-inner .stSelectbox > div > div {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            height: 44px;
        }
        
        .composer-inner .stNumberInput input {
            background-color: #F9FAFB;
            border: none;
        }
        
        .composer-inner .stNumberInput > div {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            height: 44px;
        }
        
        /* Send Button */
        .send-btn button {
            width: 44px !important;
            height: 44px !important;
            border-radius: 12px !important;
            background-color: #2563EB !important;
            color: white !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        .send-btn button:hover {
            background-color: #1D4ED8 !important;
        }
        
        /* Hide default elements */
        #MainMenu, footer, header, .stDeployButton {
            visibility: hidden;
        }
        
        /* Scrollbar hiding */
        ::-webkit-scrollbar {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

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
            
            # Parse message format: sender|ciphertext
            if '|' in received_data:
                sender, ciphertext = received_data.split('|', 1)
            else:
                # Fallback for messages without sender
                sender = st.session_state.active_chat if st.session_state.active_chat else "Partner"
                ciphertext = received_data
            
            # Decrypt the message
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
        
        # Send nickname
        sock.sendall(st.session_state.username.encode('utf-8'))
        
        st.session_state.socket = sock
        st.session_state.connected = True
        
        # Start receiver thread
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
        # Send with sender information: username|ciphertext
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
        time.sleep(1)  # Give server time to start
        return True
    except Exception as e:
        st.error(f"Failed to start server: {e}")
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
    """Display login/registration page with face recognition"""
    load_custom_css()
    
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #2E45E0;'>🔐 MSecure</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Secure Messaging Platform</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Check if we should show password reset
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
                            # Update password in users.json
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
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login", use_container_width=True, type="primary"):
                success, message = login_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error(message)
                    
                    # After 2 failed attempts, offer password reset
                    if st.session_state.login_attempts >= 2:
                        if has_face_data(username):
                            st.warning("Too many failed attempts. Redirecting to password reset...")
                            time.sleep(2)
                            st.session_state.show_reset_password = True
                            st.rerun()
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("🔐 **Privacy Notice**: Your face image will be securely stored locally for password recovery only. We respect your privacy and do not share your biometric data.")
            
            new_username = st.text_input("Username", key="reg_username")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            st.markdown("**Face ID Registration**")
            st.caption("📸 Capture your face for secure password recovery")
            
            col_cam = st.columns([1, 3, 1])
            with col_cam[1]:
                face_image = st.camera_input("Take a photo", key="reg_face", label_visibility="collapsed")
            
            consent = st.checkbox("I consent to storing my face image for password recovery purposes")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register", use_container_width=True, type="primary"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not face_image:
                    st.error("Please capture your face for registration")
                elif not consent:
                    st.error("Please consent to storing your face image")
                else:
                    success, message = register_user(new_username, new_password)
                    if success:
                        # Save face image
                        save_face_image(new_username, face_image)
                        st.success(message + " - Face data saved! You can now login")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
    
    st.markdown("<div class='auth-footer'>Made by Oussama ☕</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def render_sidebar():
    """Render custom sidebar with logo, friends list, and logout"""
    with st.sidebar:
        # Logo Row
        st.markdown("""
            <div class="sidebar-logo-row">
                <span style="font-size: 24px;">🔐</span>
                <span class="sidebar-logo-text">MSecure</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Friends Section Title
        st.markdown('<div class="sidebar-section-title">Friends</div>', unsafe_allow_html=True)
        
        # Get all registered users
        all_users = load_users()
        available_users = [user for user in all_users.keys() if user != st.session_state.username]
        
        # Set default active chat to first user if not set
        if not st.session_state.default_chat_set and available_users:
            st.session_state.active_chat = available_users[0]
            st.session_state.default_chat_set = True
            if not st.session_state.connected:
                connect_to_server()
        
        # Display users list
        for user in available_users:
            color, icon = get_user_avatar(user)
            is_active = (user == st.session_state.active_chat)
            
            # Use a container for the button to apply custom styling
            if is_active:
                st.markdown('<div class="friend-item-active">', unsafe_allow_html=True)
            else:
                st.markdown('<div>', unsafe_allow_html=True)
                
            if st.button(f"{icon}  {user}", key=f"user_{user}", use_container_width=True):
                st.session_state.active_chat = user
                if not st.session_state.connected:
                    connect_to_server()
                st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Logout Button at the bottom
        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
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
    """Render header with avatar, name, server, toggle, and status all inline"""
    recipient_name = st.session_state.active_chat if st.session_state.active_chat else "Select a friend"
    
    # Get avatar for active chat
    if st.session_state.active_chat:
        color, icon = get_user_avatar(st.session_state.active_chat)
    else:
        color, icon = "#999", "👤"
    
    status_color = "#4CAF50" if st.session_state.server_running else "#FF5252"
    status_text = "Running" if st.session_state.server_running else "Stopped"
    
    # Fixed header container
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 32px; height: 32px; border-radius: 50%; background-color: {color}; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;'>
                    {icon}
                </div>
                <div style='font-size: 16px; font-weight: 600; color: #111827;'>
                    {recipient_name}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
             st.markdown('<div style="text-align: right; padding-right: 10px; font-size: 14px; color: #374151;">Server</div>', unsafe_allow_html=True)
        with c2:
             server_toggle = st.toggle("", value=st.session_state.server_running, key="server_toggle_widget", label_visibility="collapsed")
             if server_toggle != st.session_state.server_running:
                if server_toggle:
                    start_server()
                else:
                    stop_server()
                st.session_state.server_running = server_toggle
                st.rerun()
        with c3:
             st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 6px;'>
                    <div style='background-color: {status_color}; width: 8px; height: 8px; border-radius: 50%;'></div>
                    <span style='font-size: 13px; color: #6B7280;'>{status_text}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def render_messages():
    """Render chat messages with proper layout and timestamps"""
    if not st.session_state.messages:
        st.info("No messages yet. Start chatting!")
        return
    
    # Create scrollable message container with bottom padding for fixed input
    st.markdown("<div class='messages-area'>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        sender = msg["sender"]
        is_user = (sender == st.session_state.username)
        timestamp = msg.get("timestamp", datetime.now().strftime("%I:%M %p"))
        
        if is_user:
            # Outgoing Message (Right)
            st.markdown(f"""
                <div class="message-outgoing-container">
                    <div class="message-meta">
                        <span>{timestamp}</span>
                        <span style="font-weight: 600;">You</span>
                    </div>
                    <div class="message-bubble message-outgoing">
                        {msg['text']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if msg.get("is_encrypted"):
                st.markdown(f"""
                    <div class="encrypted-chip">
                        🔒 Encrypted: {msg.get("ciphertext", "")[:50]}...
                    </div>
                """, unsafe_allow_html=True)
                
        else:
            # Incoming Message (Left)
            st.markdown(f"""
                <div class="message-incoming-container">
                    <div class="message-meta">
                        <span style="font-weight: 600;">{sender}</span>
                        <span>{timestamp}</span>
                    </div>
                    <div class="message-bubble message-incoming">
                        {msg['text']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if msg.get("is_encrypted"):
                st.markdown(f"""
                    <div class="encrypted-chip">
                        🔒 Encrypted: {msg.get("ciphertext", "")[:50]}...
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_message_input():
    """Render message input with cipher controls inline in fixed bottom container"""
    if not st.session_state.active_chat:
        st.warning("Please select a friend to chat with from the sidebar")
        return
    
    if not st.session_state.connected:
        if st.button("Connect to Chat", type="primary", use_container_width=True):
            if connect_to_server():
                st.rerun()
        return
    
    # Fixed Composer Container
    st.markdown('<div class="composer-container"><div class="composer-inner">', unsafe_allow_html=True)
    
    # Layout: Cipher (1.5) | Key (1.5) | Message (5) | Send (0.5)
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 5, 0.5])
    
    with col1:
        method = st.selectbox(
            "Cipher",
            ["caesar", "vigenere", "substitution", "transposition", "rsa", "caesar_break"],
            index=["caesar", "vigenere", "substitution", "transposition", "rsa", "caesar_break"].index(st.session_state.crypto_method),
            label_visibility="collapsed",
            key="cipher_method_select"
        )
        
        if method != st.session_state.crypto_method:
            st.session_state.crypto_method = method
            st.session_state.decryption_key = None
    
    with col2:
        # Key input based on method
        if method == "caesar":
            key = st.number_input("Key", min_value=0, max_value=25, value=3, label_visibility="collapsed")
            st.session_state.crypto_key = key
        elif method == "vigenere":
            key = st.text_input("Key", value="LEMON", label_visibility="collapsed")
            st.session_state.crypto_key = key.upper()
        elif method == "substitution":
            key = st.text_input("Key", value="QWERTYUIOPASDFGHJKLZXCVBNM", max_chars=26, label_visibility="collapsed")
            if len(key) == 26:
                st.session_state.crypto_key = key.upper()
        elif method == "transposition":
            key = st.number_input("Cols", min_value=1, value=5, label_visibility="collapsed")
            st.session_state.crypto_key = int(key)
        elif method == "rsa":
            if st.button("Gen Keys", use_container_width=True):
                public_key, private_key = generate_keypair(1024)
                st.session_state.crypto_key = public_key
                st.session_state.decryption_key = private_key
                st.success("Keys generated!")
        elif method == "caesar_break":
            key = st.number_input("Key", min_value=0, max_value=25, value=3, label_visibility="collapsed")
            st.session_state.crypto_key = key
            st.session_state.decryption_key = "english"
    
    with col3:
        message = st.text_input(
            "Message",
            key="message_input",
            placeholder="Type your message...",
            label_visibility="collapsed"
        )
    
    with col4:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        # Use native material icon if supported, otherwise fallback to unicode
        try:
            send_clicked = st.button("", icon=":material/send:", key="send_btn", help="Send message", type="primary", use_container_width=True)
        except:
            send_clicked = st.button("▶", key="send_btn", help="Send message", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if send_clicked:
            if message and message.strip():
                if send_message(message):
                    st.rerun()
                    
    st.markdown('</div></div>', unsafe_allow_html=True)

def chat_page():
    """Main chat interface"""
    load_custom_css()
    
    render_sidebar()
    render_header()
    render_messages()
    render_message_input()
    
    # Auto-refresh for new messages
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
