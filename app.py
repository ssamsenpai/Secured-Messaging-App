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
MESSAGES_FILE = 'messages.json'

# Avatar colors and icons for users
AVATAR_COLORS = ['#00C896', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#6C5CE7', '#A29BFE']
AVATAR_ICONS = ['O', 'A', 'H', 'M', 'J', 'K', 'L', 'S']

def load_messages():
    """Load all messages from the shared messages file"""
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_messages(messages):
    """Save all messages to the shared messages file"""
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        pass

def add_message(message_data):
    """Add a new message to the shared storage"""
    messages = load_messages()
    messages.append(message_data)
    save_messages(messages)
    return messages

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
    """Load custom CSS - Clean, modern layout"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; box-sizing: border-box; }
        
        /* Hide Streamlit defaults */
        .stApp { background: #F9FAFB; }
        #MainMenu, footer, header, .stDeployButton, [data-testid="stStatusWidget"] { display: none !important; }
        .main .block-container { padding: 0 !important; max-width: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* ===== SIDEBAR (260px fixed left) ===== */
        section[data-testid="stSidebar"] {
            background: #FFFFFF !important;
            width: 260px !important;
            min-width: 260px !important;
            max-width: 260px !important;
            border-right: 1px solid #E5E7EB !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding: 20px 16px !important;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        
        .sidebar-logo { text-align: center; padding-bottom: 20px; border-bottom: 1px solid #E5E7EB; margin-bottom: 16px; }
        .sidebar-logo img { width: 140px; height: auto; }
        
        .sidebar-section-title { font-size: 11px; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
        
        /* Friend buttons in sidebar */
        section[data-testid="stSidebar"] .stButton button {
            background: transparent !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            color: #1F2937 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            margin-bottom: 6px !important;
            transition: all 0.15s ease !important;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background: rgba(0,200,150,0.08) !important;
            border-color: #00C896 !important;
        }
        section[data-testid="stSidebar"] .stButton button:active {
            background: rgba(0,200,150,0.15) !important;
        }
        
        /* Active friend button */
        section[data-testid="stSidebar"] .stButton button[kind="secondary"]:has(🟢) {
            background: rgba(0,200,150,0.12) !important;
            border-color: #00C896 !important;
            color: #00C896 !important;
        }
        
        /* ===== MAIN CONTENT (right of sidebar) ===== */
        .main > div:first-child { margin-left: 0 !important; }
        
        /* ===== HEADER (fixed top, 56px) ===== */
        .app-header {
            position: fixed;
            top: 0;
            left: 260px;
            right: 0;
            height: 56px;
            background: #FFFFFF;
            border-bottom: 1px solid #E5E7EB;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 100;
        }
        
        .header-user { display: flex; align-items: center; gap: 12px; }
        .header-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 15px; }
        .header-name { font-size: 15px; font-weight: 600; color: #1F2937; }
        
        .server-label { font-size: 13px; color: #6B7280; margin-bottom: 4px; display: block; }
        .server-status { font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 4px; }
        
        /* Refresh button */
        .app-header .stButton button {
            background: transparent !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            padding: 6px 10px !important;
            font-size: 16px !important;
            min-height: 36px !important;
            height: 36px !important;
        }
        .app-header .stButton button:hover { background: #F3F4F6 !important; }
        
        /* ===== MESSAGES AREA (scrollable, between header and composer) ===== */
        .messages-area {
            position: fixed;
            top: 56px;
            left: 260px;
            right: 0;
            bottom: 100px;
            background: #F9FAFB;
            padding: 20px 24px;
            overflow-y: auto;
            overflow-x: hidden;
        }
        
        .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }
        .empty-icon { font-size: 64px; margin-bottom: 16px; }
        .empty-state h3 { font-size: 18px; font-weight: 600; color: #1F2937; margin: 0 0 8px 0; }
        .empty-state p { font-size: 14px; color: #9CA3AF; margin: 0; }
        
        /* Message bubbles */
        .msg { display: flex; gap: 10px; margin-bottom: 16px; }
        .msg.outgoing { flex-direction: row-reverse; }
        
        .msg-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px; flex-shrink: 0; }
        .msg-body { max-width: 60%; }
        .msg-meta { font-size: 12px; color: #6B7280; margin-bottom: 4px; }
        .msg.outgoing .msg-meta { text-align: right; }
        
        .msg-bubble { padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; word-break: break-word; }
        .msg.incoming .msg-bubble { background: #FFFFFF; border: 1px solid #E5E7EB; border-bottom-left-radius: 4px; }
        .msg.outgoing .msg-bubble { background: rgba(0,200,150,0.12); border-bottom-right-radius: 4px; }
        
        .encrypted-badge { font-size: 11px; color: #9CA3AF; margin-left: 8px; cursor: pointer; position: relative; display: inline-block; }
        .encrypted-badge:hover { color: #00C896; }
        .encrypted-badge .cipher-tooltip {
            visibility: hidden; opacity: 0; position: absolute; bottom: 120%; left: 50%; transform: translateX(-50%);
            background: #1F2937; color: #FFF; padding: 8px 12px; border-radius: 6px; font-size: 11px;
            white-space: nowrap; max-width: 300px; overflow: hidden; text-overflow: ellipsis; z-index: 1000;
            transition: opacity 0.2s, visibility 0.2s;
        }
        .encrypted-badge .cipher-tooltip::after {
            content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
            border: 6px solid transparent; border-top-color: #1F2937;
        }
        .encrypted-badge:hover .cipher-tooltip { visibility: visible; opacity: 1; }
        
        /* ===== COMPOSER (fixed bottom, ~100px) ===== */
        .composer-container {
            position: fixed;
            bottom: 0;
            left: 260px;
            right: 0;
            background: #FFFFFF;
            border-top: 1px solid #E5E7EB;
            padding: 16px 24px;
            z-index: 100;
        }
        
        .composer-placeholder { text-align: center; color: #9CA3AF; margin: 0; }
        
        .composer-container .stSelectbox,
        .composer-container .stNumberInput,
        .composer-container .stTextInput { margin-bottom: 0 !important; }
        
        .composer-container .stSelectbox > div,
        .composer-container .stNumberInput > div,
        .composer-container .stTextInput > div { margin-bottom: 0 !important; }
        
        .composer-container .stSelectbox label,
        .composer-container .stNumberInput label { font-size: 11px !important; color: #6B7280 !important; margin-bottom: 4px !important; }
        
        .composer-container .stTextInput label { display: none !important; }
        
        .composer-container .stTextInput input {
            height: 44px !important; border-radius: 8px !important; border: 1px solid #E5E7EB !important; padding: 0 14px !important;
        }
        .composer-container .stTextInput input:focus { border-color: #00C896 !important; box-shadow: 0 0 0 1px #00C896 !important; }
        
        .composer-container .stButton button {
            height: 44px !important; min-height: 44px !important; border-radius: 8px !important;
            background: #00C896 !important; color: white !important; border: none !important;
            font-size: 18px !important; font-weight: 600 !important;
        }
        .composer-container .stButton button:hover { background: #00A87D !important; }
        
        /* Toggle (green only) */
        [data-testid="stToggle"] span[data-checked="true"] { background-color: #00C896 !important; }
        [data-testid="stToggle"] label { display: none !important; }
        
        /* ===== LOGIN PAGE ===== */
        [data-testid="stSidebar"]:has(~ .main .login-page) { display: none !important; }
        
        .login-page { max-width: 400px; margin: 0 auto; padding: 60px 20px; }
        .login-logo { text-align: center; margin-bottom: 32px; }
        .login-logo img { width: 160px; height: auto; }
        .login-title { text-align: center; font-size: 24px; font-weight: 700; color: #1F2937; margin-bottom: 8px; }
        .login-subtitle { text-align: center; font-size: 14px; color: #6B7280; margin-bottom: 32px; }
        
        .login-page .stButton button { background: #00C896 !important; color: white !important; border: none !important; border-radius: 8px !important; height: 44px !important; font-weight: 600 !important; }
        .login-page .stButton button:hover { background: #00A87D !important; }
        
        .login-page .stTextInput input { border-radius: 8px !important; height: 44px !important; border: 1px solid #E5E7EB !important; }
        .login-page .stTextInput input:focus { border-color: #00C896 !important; box-shadow: 0 0 0 1px #00C896 !important; }
        
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
if 'reset_username' not in st.session_state:
    st.session_state.reset_username = None

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
            
            # Parse: sender|recipient|ciphertext
            parts = received_data.split('|')
            if len(parts) >= 3:
                sender, recipient, ciphertext = parts[0], parts[1], '|'.join(parts[2:])
            elif len(parts) == 2:
                sender, ciphertext = parts[0], parts[1]
                recipient = st.session_state.username
            else:
                sender = "Unknown"
                ciphertext = received_data
                recipient = st.session_state.username
            
            # Only process if message is for us
            if recipient != st.session_state.username:
                continue
            
            try:
                d_key = st.session_state.decryption_key if st.session_state.decryption_key is not None else st.session_state.crypto_key
                plaintext = decrypt(ciphertext, d_key, st.session_state.crypto_method)
                
                msg_data = {
                    "sender": sender,
                    "recipient": st.session_state.username,
                    "text": plaintext,
                    "ciphertext": ciphertext,
                    "is_encrypted": True,
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                # Save to shared file
                add_message(msg_data)
                
                # Update local session
                st.session_state.messages.append(msg_data)
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
        message_with_sender = f"{st.session_state.username}|{st.session_state.active_chat}|{ciphertext}"
        st.session_state.socket.sendall(message_with_sender.encode('utf-8'))
        
        # Create message data
        msg_data = {
            "sender": st.session_state.username,
            "recipient": st.session_state.active_chat,
            "text": message,
            "ciphertext": ciphertext,
            "is_encrypted": True,
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Save to shared file for persistence
        add_message(msg_data)
        
        # Also update local session state
        st.session_state.messages.append(msg_data)
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
    # Add login-view class to body
    st.markdown('<style>.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }</style>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Display logo at top
    logo_path = os.path.join(os.getcwd(), "Msecure logo.svg")
    if os.path.exists(logo_path):
        with open(logo_path, 'r') as f:
            logo_svg = f.read()
            import base64
            logo_b64 = base64.b64encode(logo_svg.encode()).decode()
            st.markdown(f"""
                <div style="text-align: center; padding: 40px 0 20px 0;">
                    <img src="data:image/svg+xml;base64,{logo_b64}" style="width: 180px; height: auto;" alt="MSecure Logo"/>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #00C896; margin-top: 60px;'>🔐 MSecure</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #6B7280; margin-bottom: 40px;'>Secure Messaging Platform</h3>", unsafe_allow_html=True)
    
    if st.session_state.show_reset_password:
        st.subheader("Reset Password with Face Verification")
        
        # Prefill username from the last failed login
        reset_username_prefill = st.session_state.reset_username or ""
        reset_username = st.text_input("Username", value=reset_username_prefill, key="reset_username_field", disabled=bool(reset_username_prefill))
        st.session_state.reset_username = reset_username
        
        if reset_username:
            if has_face_data(reset_username):
                st.info("📸 Please capture your face to verify your identity")
                
                face_image = st.camera_input("Take a photo", key="reset_face")
                
                if face_image:
                    if verify_face_image(reset_username, face_image):
                        st.success("✅ Face verified! Enter a new password")
                        
                        new_password = st.text_input("New Password", type="password", key="new_pass")
                        confirm_new = st.text_input("Confirm New Password", type="password", key="confirm_new")
                        
                        if st.button("Reset Password", use_container_width=True):
                            if new_password == confirm_new and len(new_password) >= 6:
                                from auth import hash_password, save_users
                                users = load_users()
                                users[reset_username] = hash_password(new_password)
                                save_users(users)
                                
                                st.success("Password reset successful! Please log in with your new password.")
                                st.session_state.show_reset_password = False
                                st.session_state.login_attempts = 0
                                st.session_state.reset_username = None
                                time.sleep(1.5)
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
            st.session_state.reset_username = None
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
                    st.session_state.reset_username = None
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error(message)
                    
                    if st.session_state.login_attempts >= 2:
                        if has_face_data(username):
                            st.session_state.reset_username = username
                            st.warning("Too many failed attempts. Redirecting to password reset with Face ID...")
                            time.sleep(1.5)
                            st.session_state.show_reset_password = True
                            st.session_state.login_attempts = 0
                            st.rerun()
                        else:
                            st.info("No face data found for this user. Please register Face ID or contact support.")
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with logo, friends list, and logout"""
    
    def get_avatar_color(username):
        colors = ['#00C896', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
        return colors[sum(ord(c) for c in username) % len(colors)]
    
    with st.sidebar:
        # Logo
        logo_path = os.path.join(os.getcwd(), "Msecure logo.svg")
        if os.path.exists(logo_path):
            with open(logo_path, 'r') as f:
                import base64
                logo_b64 = base64.b64encode(f.read().encode()).decode()
                st.markdown(f'<div class="sidebar-logo"><img src="data:image/svg+xml;base64,{logo_b64}" alt="MSecure"/></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sidebar-logo"><h2 style="color:#00C896;">🔐 MSecure</h2></div>', unsafe_allow_html=True)
        
        # Friends section
        st.markdown('<div class="sidebar-section-title">Friends</div>', unsafe_allow_html=True)
        
        all_users = load_users()
        available_users = [u for u in all_users.keys() if u != st.session_state.username]
        
        if not st.session_state.default_chat_set and available_users:
            st.session_state.active_chat = available_users[0]
            st.session_state.default_chat_set = True
        
        # Friend list - each friend is a button with avatar and name inside
        for user in available_users:
            is_active = user == st.session_state.active_chat
            color = get_avatar_color(user)
            
            # Create button with custom label containing avatar + name
            btn_label = f"🟢 {user}" if is_active else user
            if st.button(btn_label, key=f"friend_{user}", use_container_width=True):
                st.session_state.active_chat = user
                if not st.session_state.connected:
                    connect_to_server()
                st.rerun()
            
            # Inject avatar styling via CSS class
            if is_active:
                st.markdown(f'<style>[data-testid="stButton"][key="friend_{user}"] button {{ background: rgba(0,200,150,0.12) !important; }}</style>', unsafe_allow_html=True)
        
        # Spacer
        st.markdown('<div style="flex:1;"></div>', unsafe_allow_html=True)
        
        # Logout at bottom
        if st.button("🚪 Logout", key="logout", use_container_width=True):
            if st.session_state.connected:
                disconnect_from_server()
            if st.session_state.server_running:
                stop_server()
            for key in ['authenticated', 'username', 'active_chat', 'default_chat_set', 'messages']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def render_header():
    """Render fixed header with chat info, server toggle and refresh"""
    active = st.session_state.active_chat or "Select a friend"
    
    def get_avatar_color(username):
        colors = ['#00C896', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
        return colors[sum(ord(c) for c in username) % len(colors)]
    
    avatar_letter = active[0].upper() if st.session_state.active_chat else "?"
    avatar_color = get_avatar_color(active) if st.session_state.active_chat else "#9CA3AF"
    status_text = "● Running" if st.session_state.server_running else "○ Stopped"
    status_color = "#00C896" if st.session_state.server_running else "#EF4444"
    
    # Use columns for layout: Avatar+Name | Spacer | Server Toggle | Status | Refresh
    col1, col2, col3, col4, col5 = st.columns([3, 4, 1.5, 1.5, 0.8])
    
    with col1:
        st.markdown(f'''
            <div class="header-user">
                <div class="header-avatar" style="background:{avatar_color}">{avatar_letter}</div>
                <span class="header-name">{active}</span>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<span class="server-label">Server</span>', unsafe_allow_html=True)
        server_toggle = st.toggle("", value=st.session_state.server_running, key="server_toggle")
        if server_toggle != st.session_state.server_running:
            if server_toggle:
                start_server()
            else:
                stop_server()
            st.session_state.server_running = server_toggle
            st.rerun()
    
    with col4:
        st.markdown(f'<span class="server-status" style="color:{status_color}">{status_text}</span>', unsafe_allow_html=True)
    
    with col5:
        if st.button("🔄", key="refresh_btn", help="Refresh messages"):
            st.rerun()

def render_messages():
    """Render scrollable messages area"""
    def get_avatar_color(username):
        colors = ['#00C896', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']
        return colors[sum(ord(c) for c in username) % len(colors)]
    
    active = st.session_state.active_chat
    current_user = st.session_state.username
    
    # Load messages from shared file and merge with session state
    all_messages = load_messages()
    
    # Filter messages for active chat (between me and active_chat)
    filtered = [
        m for m in all_messages
        if (m.get("sender") == current_user and m.get("recipient") == active)
        or (m.get("sender") == active and m.get("recipient") == current_user)
    ] if active else []
    
    if not filtered:
        st.markdown(f'''
            <div class="empty-state">
                <div class="empty-icon">💬</div>
                <h3>Start a conversation{f" with {active}" if active else ""}</h3>
                <p>Send a message to begin your encrypted chat</p>
            </div>
        ''', unsafe_allow_html=True)
    else:
        for msg in filtered:
            sender = msg["sender"]
            is_mine = sender == current_user
            ts = msg.get("timestamp", datetime.now().strftime("%I:%M %p"))
            label = "You" if is_mine else sender
            color = get_avatar_color(sender)
            letter = sender[0].upper()
            cls = "outgoing" if is_mine else "incoming"
            
            # Build encrypted badge with tooltip showing ciphertext
            if msg.get("is_encrypted"):
                ciphertext = msg.get("ciphertext", "[encrypted]")
                # Truncate if too long
                display_cipher = ciphertext[:50] + "..." if len(ciphertext) > 50 else ciphertext
                encrypted = f'<span class="encrypted-badge" title="Click to see encrypted">🔒<span class="cipher-tooltip">{display_cipher}</span></span>'
            else:
                encrypted = ''
            
            st.markdown(f'''
                <div class="msg {cls}">
                    <div class="msg-avatar" style="background:{color}">{letter}</div>
                    <div class="msg-body">
                        <div class="msg-meta">{label} · {ts}</div>
                        <div class="msg-bubble">{msg['text']}{encrypted}</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

def render_message_input():
    """Render fixed composer with cipher selector, key, message, and send button"""
    if not st.session_state.active_chat:
        st.markdown('<p class="composer-placeholder">Select a friend to start chatting</p>', unsafe_allow_html=True)
        return
    
    if not st.session_state.connected:
        if st.button("🔌 Connect to Chat", key="connect_btn", use_container_width=True):
            if connect_to_server():
                st.rerun()
        return
    
    # Single row with all controls
    col1, col2, col3, col4 = st.columns([1.5, 1.2, 5.5, 0.8])
    
    with col1:
        method = st.selectbox(
            "Cipher",
            ["caesar", "vigenere", "substitution", "transposition", "rsa", "caesar_break"],
            index=["caesar", "vigenere", "substitution", "transposition", "rsa", "caesar_break"].index(st.session_state.crypto_method),
            key="cipher_method"
        )
        if method != st.session_state.crypto_method:
            st.session_state.crypto_method = method
            st.session_state.decryption_key = None
    
    with col2:
        if method == "caesar":
            key = st.number_input("Key", min_value=0, max_value=25, value=3, key="caesar_key_input")
            st.session_state.crypto_key = key
        elif method == "vigenere":
            key = st.text_input("Key", value="LEMON", key="vig_key")
            st.session_state.crypto_key = key.upper()
        elif method == "substitution":
            key = st.text_input("Key", value="QWERTY...", max_chars=26, key="sub_key")
            if len(key) == 26:
                st.session_state.crypto_key = key.upper()
        elif method == "transposition":
            key = st.number_input("Cols", min_value=1, value=5, key="trans_key")
            st.session_state.crypto_key = int(key)
        elif method == "rsa":
            if st.button("🔑 Gen", key="gen_rsa_keys", use_container_width=True):
                public_key, private_key = generate_keypair(1024)
                st.session_state.crypto_key = public_key
                st.session_state.decryption_key = private_key
        elif method == "caesar_break":
            key = st.number_input("Key", min_value=0, max_value=25, value=3, key="break_key")
            st.session_state.crypto_key = key
            st.session_state.decryption_key = "english"
    
    with col3:
        message = st.text_input("Message", key="message_input", placeholder="Write your message here..")
    
    with col4:
        send_clicked = st.button("➤", key="send_btn", use_container_width=True)
        if send_clicked and message and message.strip():
            if send_message(message):
                st.rerun()

def chat_page():
    """Main chat interface with fixed header, scrollable chat, fixed composer"""
    load_custom_css()
    
    # Render sidebar (fixed left)
    render_sidebar()
    
    # Main content area (right of sidebar)
    # Header - fixed at top
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    render_header()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Messages area - scrollable
    st.markdown('<div class="messages-area">', unsafe_allow_html=True)
    render_messages()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Composer - fixed at bottom
    st.markdown('<div class="composer-container">', unsafe_allow_html=True)
    render_message_input()
    st.markdown('</div>', unsafe_allow_html=True)
    
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
