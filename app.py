import streamlit as st
from database import Session
from utils import login_user, logout

st.set_page_config(page_title="Agri Equipment Rental", layout="wide")

# Initialize session
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Sidebar navigation
menu = ["Home", "Login", "Register", "List Equipment", "Search Equipment", "My Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# Page routing
if choice == "Home":
    st.title("🌾 Smart Agri Equipment Rental Platform")
    st.write("Connect farmers with machinery they need.")

elif choice == "Login":
    # Login form
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            session = Session()
            if login_user(username, password, session):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

elif choice == "Register":
    # Registration form
    with st.form("register"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        role = st.selectbox("I am a", ["renter", "owner"])
        location = st.text_input("Your location (city/area)")
        submitted = st.form_submit_button("Register")
        if submitted:
            session = Session()
            # Check if user exists
            if session.query(User).filter_by(username=username).first():
                st.error("Username already exists")
            else:
                new_user = User(
                    username=username,
                    password=hash_password(password),
                    email=email,
                    role=role,
                    location=location
                )
                session.add(new_user)
                session.commit()
                st.success("Registration successful! Please login.")
