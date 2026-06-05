import streamlit as st
import hashlib
import os
import database

def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC with SHA-256 and a random salt.
    """
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{hash_bytes.hex()}"

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """
    Verify a password against a stored PBKDF2-HMAC hash.
    """
    try:
        salt_hex, hash_hex = stored_password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        hash_bytes = bytes.fromhex(hash_hex)
        new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_hash == hash_bytes
    except Exception:
        return False

def register_user(username, password, name):
    """
    Register a new user.
    """
    username = username.strip()
    name = name.strip()
    if not username or not password or not name:
        return False, "All fields are required."
    
    password_hash = hash_password(password)
    user_id = database.create_user(username, password_hash, name)
    if user_id is None:
        return False, "Username already exists."
    
    # Pre-populate empty health profile on registration
    database.save_health_profile(
        user_id=user_id,
        age=25,
        gender="Male",
        height=175.0,
        weight=70.0,
        goal="Maintenance",
        activity_level="Moderately Active",
        allergies="",
        dietary_preferences="Non-Vegetarian",
        medical_conditions="",
        fitness_experience="Beginner"
    )
    
    return True, "Registration successful. You can now log in."

def login_user(username, password):
    """
    Log in a user and set up session states.
    """
    username = username.strip()
    if not username or not password:
        return False, "All fields are required."
    
    user = database.get_user_by_username(username)
    if user and verify_password(user['password_hash'], password):
        st.session_state['user_id'] = user['id']
        st.session_state['username'] = user['username']
        st.session_state['name'] = user['name']
        return True, "Login successful."
    return False, "Invalid username or password."

def logout_user():
    """
    Clear session states and log out user.
    """
    for key in ['user_id', 'username', 'name']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def is_logged_in():
    """
    Check if a user session is active.
    """
    return 'user_id' in st.session_state

def get_current_user_id():
    """
    Retrieve the current logged-in user's ID.
    """
    return st.session_state.get('user_id')
