import bcrypt
import streamlit as st

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login_user(username, password, session):
    user = session.query(User).filter_by(username=username).first()
    if user and check_password(password, user.password):
        st.session_state['user'] = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'location': user.location
        }
        return True
    return False

def logout():
    st.session_state.clear()
