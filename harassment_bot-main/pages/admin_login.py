import streamlit as st
import bcrypt
import re
import pymongo 
from pymongo.mongo_client import MongoClient
from gridfs import GridFS
import pandas as pd
import numpy as np

uri = "mongodb+srv://saikiranpatnana:mayya143@saikiran.bdu0jbl.mongodb.net/?retryWrites=true&w=majority&appName=saikiran"
client=MongoClient(uri)
db=client.test
collection = db['harassement_admin']
fs = GridFS(db)

if "page" not in st.session_state:
    st.session_state["page"] = "Login" 
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    
fs = GridFS(db)
def retrieve_pdf(pdf_id):
    pdf_data = fs.get(pdf_id)
    with open('retrieved_output.pdf', 'wb') as file:
        file.write(pdf_data.read())
    print("PDF retrieved and saved as 'retrieved_output.pdf'")

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
                st.session_state["username"] = username 
                st.success(result["message"])
                navigate_to("Dashboard")
            else:
                st.error(result["message"])
    
    if st.button("Go to Sign Up"):
        st.session_state["page"] = "Signup"
        st.experimental_rerun()


def is_password_valid(password):
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
        rows = []
    collection = db['harassment_register']
    for record in collection.find():
        if len(record.items()) == 7:
            row = {
                'STUDENT_ID': record.get('student_id', None),
                'TOKEN' : record.get('token', None),
                'LEVEL': record.get('level', None),
                'REPORTED_TIMESTAMP': record.get('reported_timestamp', None),
                'COMPLAINT_ID': record.get('pdf_id', None)
                }
            rows.append(row)
    df = pd.DataFrame(rows)
    print(df)
    st.dataframe(rows,  use_container_width=True)
    student_id = st.text_input("Enter the Student ID to get her Details:")
    data = pd.read_csv('data.csv').set_index('ID_No')
    if student_id:
        if student_id in data.index and student_id in list(df['STUDENT_ID']):  # Check if the student_id exists in the index
            student_data = data.loc[student_id]
            
            # Use an expander to show details
            with st.expander(f"Details for Student ID: {student_id}", expanded=True):
                st.write(f"**Name:** {student_data['Name']}")
                st.write(f"**Course:** {student_data['Course']}")
                st.write(f"**Branch:** {student_data['Branch']}")
                st.write(f"**Year:** {student_data['Year']}")
                st.write(f"**Mobile:** {student_data['Mobile']}")
        else:
            st.error("Student ID not found.")

    pdf_id = st.text_input("Enter the Complaint ID to download the complaint:")
    if pdf_id:
        pdf_ids = list(str(pdf_id) for pdf_id in df['COMPLAINT_ID'])
        if pdf_id!= '' and pdf_id in pdf_ids:
            # Retrieve the PDF
            pdf_id_str = pdf_id
            pdf_id = [id for id in df['COMPLAINT_ID'] if str(id) == pdf_id][0]
            print(pdf_id, type(pdf_id))
            retrieve_pdf(pdf_id)
            
            with open("retrieved_output.pdf", "rb") as file:
                pdf_data = file.read()
            
            st.download_button(
                label="Download Complaint PDF",
                data=pdf_data,
                file_name=f"{pdf_id_str}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Invalid Complaint ID!")
            
if st.session_state["page"] == "Login":
    login_page()
elif st.session_state["page"] == "Signup":
    signup_page()
elif st.session_state["page"] == "Dashboard":
    admin_dashboard()
