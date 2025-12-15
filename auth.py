# auth.py
# Authentication system with bcrypt password hashing
import bcrypt
import json
import os
from typing import Optional, Dict

USERS_DB = "users.json"

def load_users() -> Dict[str, str]:
    """Load users from JSON file. Returns dict of username -> hashed_password"""
    if not os.path.exists(USERS_DB):
        return {}
    try:
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users: Dict[str, str]) -> bool:
    """Save users to JSON file"""
    try:
        with open(USERS_DB, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success, message)
    """
    if not username or not password:
        return False, "Username and password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    # Hash the password
    hashed = hash_password(password)
    users[username] = hashed
    
    if save_users(users):
        return True, "Registration successful"
    else:
        return False, "Error saving user data"

def login_user(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate a user.
    Returns (success, message)
    """
    if not username or not password:
        return False, "Username and password cannot be empty"
    
    users = load_users()
    
    if username not in users:
        return False, "Invalid username or password"
    
    hashed = users[username]
    
    if verify_password(password, hashed):
        return True, "Login successful"
    else:
        return False, "Invalid username or password"

def user_exists(username: str) -> bool:
    """Check if a user exists"""
    users = load_users()
    return username in users
