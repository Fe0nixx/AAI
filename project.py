import streamlit as st
import pandas as pd
import hashlib
import os
import json
import plotly.express as px

# File paths
USER_DB_FILE = "C://Users//Siddharth//OneDrive//Desktop//streamlit//users.json"
MARKS_DB_FILE = "C://Users//Siddharth//OneDrive//Desktop//streamlit//marks.csv"

# Helper function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load users from the JSON file
def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

# Save users to the JSON file
def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

# Check if email is already registered
def is_email_registered(email):
    users = load_users()
    return email in users

# Authenticate user during login
def authenticate(email, password):
    users = load_users()
    hashed_password = hash_password(password)
    return users.get(email) == hashed_password

# Save marks to a CSV file
def save_marks(name, email, aai, foml, imad, vcc):
    marks_data = {
        "name": name,
        "email": email,
        "AAI": aai,
        "FOML": foml,
        "IMAD": imad,
        "VCC": vcc
    }
    if os.path.exists(MARKS_DB_FILE):
        marks_df = pd.read_csv(MARKS_DB_FILE)
    else:
        marks_df = pd.DataFrame(columns=["name", "email", "AAI", "FOML", "IMAD", "VCC"])
    
    new_marks_df = pd.DataFrame([marks_data])
    marks_df = pd.concat([marks_df, new_marks_df], ignore_index=True)
    marks_df.to_csv(MARKS_DB_FILE, index=False)

# Check if user has already submitted marks
def has_submitted_marks(email):
    if os.path.exists(MARKS_DB_FILE):
        marks_df = pd.read_csv(MARKS_DB_FILE)
        return not marks_df[marks_df["email"] == email].empty
    return False

# Plotting functions using Plotly
def plot_graphs(email):
    if not os.path.exists(MARKS_DB_FILE):
        st.warning("No marks data available.")
        return

    marks_df = pd.read_csv(MARKS_DB_FILE)
    user_marks = marks_df[marks_df["email"] == email]

    if user_marks.empty:
        st.warning("No marks found for this user.")
        return

    # Use the latest marks only
    latest_marks = user_marks.iloc[-1]

    subjects = ["AAI", "FOML", "IMAD", "VCC"]
    marks = [latest_marks["AAI"], latest_marks["FOML"], latest_marks["IMAD"], latest_marks["VCC"]]

    # Bar chart (average marks)
    st.subheader("Marks per Subject")
    st.plotly_chart(px.bar(x=subjects, y=marks, labels={'x': 'Subject', 'y': 'Marks'}, title="Marks per Subject"))

    # Line graph (marks per subject)
    st.subheader("Marks per Subject")
    st.plotly_chart(px.line(x=subjects, y=marks, labels={'x': 'Subject', 'y': 'Marks'}, title="Marks per Subject"))

    # Pie chart (marks distribution)
    st.subheader("Marks Distribution")
    st.plotly_chart(px.pie(values=marks, names=subjects, title="Marks Distribution"))

# Session state for managing authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None

# Signup function
def signup():
    st.title("Sign Up")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if is_email_registered(email):
            st.warning("This email is already registered. Please log in.")
        else:
            hashed_password = hash_password(password)
            users = load_users()
            users[email] = hashed_password  # Store email and hashed password
            save_users(users)  # Save updated users
            st.success("Successfully signed up! Please log in.")
            st.session_state.authenticated = False

# Login function
def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(email, password):
            st.session_state.authenticated = True
            st.session_state.current_user = email
            st.session_state.current_user_name = email  # Use email or modify as needed
            st.success(f"Welcome, {st.session_state.current_user_name}!")

            # Check if the user has already submitted marks
            if has_submitted_marks(email):
                st.success("You have already submitted your marks.")
                plot_graphs(email)  # Show graphs directly
            else:
                st.session_state.has_submitted_marks = False  # Marks not yet submitted
        else:
            st.error("Invalid email or password")

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_user_name = None
    st.success("You have been logged out.")

# Main app logic
if not st.session_state.authenticated:
    st.sidebar.title("Authentication")
    auth_action = st.sidebar.radio("Choose", ["Login", "Sign Up"])
    
    if auth_action == "Login":
        login()
    else:
        signup()
else:
    st.sidebar.title(f"Welcome, {st.session_state.current_user_name}")
    if st.sidebar.button("Log Out"):
        logout()

    st.title(f"Welcome, {st.session_state.current_user_name}!")

    # Marks input sliders only if marks have not been submitted
    if not has_submitted_marks(st.session_state.current_user):
        st.subheader("Enter Your Marks")
        aai = st.slider("AAI", 0, 100, 50)
        foml = st.slider("FOML", 0, 100, 50)
        imad = st.slider("IMAD", 0, 100, 50)
        vcc = st.slider("VCC", 0, 100, 50)

        if st.button("Submit Marks"):
            save_marks(st.session_state.current_user_name, st.session_state.current_user, aai, foml, imad, vcc)
            st.success("Marks submitted successfully!")
            plot_graphs(st.session_state.current_user)  # Show graphs after submission
    else:
        st.success("You have already submitted your marks.")
        plot_graphs(st.session_state.current_user)  # Show graphs directly
