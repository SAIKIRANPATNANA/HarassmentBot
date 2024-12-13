import streamlit as st
import bcrypt
from pymongo import MongoClient
import re
import pymongo 
from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://saikiranpatnana:mayya143@saikiran.bdu0jbl.mongodb.net/?retryWrites=true&w=majority&appName=saikiran"
client=MongoClient(uri)
db=client.test
collection=db['harassment_admin']

if "page" not in st.session_state:
    st.session_state["page"] = "Login" 
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def navigate_to(page):
    st.session_state["page"] = page
    st.experimental_rerun()


def create_user(username, password):
    
    if collection.find_one({"username": username}):
        return {"success": False, "message": "Username already exists!"}
    
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    
    
    user_data = {
        "username": username,
        "password": hashed_password.decode("utf-8"),  
        "role": "admin" 
    }

    collection.insert_one(user_data)
    return {"success": True, "message": "Account created successfully!"}


def login_user(username, password):
    """
    Authenticate the user by validating credentials.

    Args:
    - username (str): The input username.
    - password (str): The input password.

    Returns:
    - dict: Result of authentication with success flag and message.
    """
    # Fetch user from MongoDB
    user = collection.find_one({"username": username})
    if not user:
        return {"success": False, "message": "Username does not exist!"}
    
    # Check password
    stored_hashed_password = user["password"].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password):
        return {"success": True, "message": "Login successful!"}
    else:
        return {"success": False, "message": "Invalid password!"}

def login_page():
    st.title("Admin Login")
    st.write("Log in to access the Admin Dashboard.")
    
    with st.form("Login Form"):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Log In")
        
        if login_button:
            result = login_user(username, password)
            if result["success"]:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username  # Store username for personalization
                st.success(result["message"])
                navigate_to("Dashboard")
            else:
                st.error(result["message"])
    
    if st.button("Go to Sign Up"):
        st.session_state["page"] = "Signup"
        st.experimental_rerun()


def is_password_valid(password):
    """
    Validate the password against the complexity requirements.
    - At least one uppercase letter.
    - At least one lowercase letter.
    - At least one digit.
    - At least one special character.
    - Minimum length of 8.
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long!"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter!"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter!"
    if not re.search(r"\d", password):
        return "Password must contain at least one number!"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character!"
    return None

def signup_page():
    st.title("Admin Signup")
    st.write("Create an account to manage the admin dashboard.")
    
    with st.form("Signup Form"):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_button = st.form_submit_button("Sign Up")
        
        if signup_button:
            # Validate username
            if not username.strip():
                st.error("Username cannot be empty!")
                return
            
            # Validate password
            if not password.strip():
                st.error("Password cannot be empty!")
                return
            
            password_validation_error = is_password_valid(password)
            if password_validation_error:
                st.error(password_validation_error)
                return
            
            # Check if passwords match
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            
            # Proceed with user creation
            result = create_user(username, password)
            if result["success"]:
                st.success(result["message"])
                st.session_state["signup_success"] = True  # Set session flag
                navigate_to("Login")
            else:
                st.error(result["message"])
    
    # Post-signup success navigation
    if st.session_state.get("signup_success"):
        if st.button("Go to Login"):
            st.session_state["page"] = "Login"
            st.experimental_rerun()

def admin_dashboard():
    st.title("Admin Dashboard")
    if not st.session_state["logged_in"]:
        st.warning("You must log in to access the dashboard.")
        navigate_to("Login")
    else:
        st.write("Welcome to the Admin Dashboard!")

        if st.button("Log Out"):
            st.session_state["logged_in"] = False
            navigate_to("Login")

if st.session_state["page"] == "Login":
    login_page()
elif st.session_state["page"] == "Signup":
    signup_page()
elif st.session_state["page"] == "Dashboard":
    admin_dashboard()
