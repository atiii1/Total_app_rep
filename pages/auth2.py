import streamlit as st
import bcrypt
import streamlit_authenticator as stauth
import sqlite3

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
          CREATE TABLE IF NOT EXISTS users
          (username TEXT PRIMARY KEY, 
          name TEXT, 
          password TEXT)
          ''')
conn.commit()

# Hash passwords using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Add new user to the database
def add_user(username, name, password):
    try:
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, name, password) VALUES (?, ?, ?)", 
                  (username, name, hashed_pw))
        conn.commit()
        st.success(f"User {username} added successfully!")
        st.write(f"User {username} added to database with hashed password: {hashed_pw}.")
    except sqlite3.IntegrityError:
        st.error("Username already exists")
    except Exception as e:
        st.error(f"Error adding user: {e}")

# Fetch user credentials from the database
def fetch_credentials():
    c.execute("SELECT username, name, password FROM users")
    users = c.fetchall()
    credentials = {
        "usernames": {
            user[0]: {"name": user[1], "password": user[2]} for user in users
        }
    }
    st.write("Fetched credentials:", credentials)  # Debugging line to display credentials
    return credentials

# Initialize authenticator
def initialize_authenticator():
    credentials = fetch_credentials()
    return stauth.Authenticate(
        credentials,
        "some_cookie_name",
        "some_signature_key",
        cookie_expiry_days=30
    )

# Global variable to store the authenticator
authenticator = initialize_authenticator()

# User Registration
def register_user():
    st.sidebar.title("Create a New Account")
    new_username = st.sidebar.text_input("Enter a username")
    new_name = st.sidebar.text_input("Enter your name")
    new_password = st.sidebar.text_input("Enter a password", type="password")
    confirm_password = st.sidebar.text_input("Confirm your password", type="password")
    
    if st.sidebar.button("Register"):
        if new_password == confirm_password:
            add_user(new_username, new_name, new_password)
            # Reinitialize the authenticator with updated credentials
            global authenticator
            authenticator = initialize_authenticator()
            st.sidebar.success(f"Account for {new_username} created successfully!")
        else:
            st.sidebar.error("Passwords do not match!")

# Show registration option
if st.sidebar.button("Sign up"):
    register_user()

# Debugging: Print the contents of the database
c.execute("SELECT * FROM users")
st.write("Current users in database:", c.fetchall())

# Login widget with fields parameter
fields = {
    "Form name": "Login",
    "Username": "Username",
    "Password": "Password",
    "Login": "Login"
}

try:
    name, authentication_status, username = authenticator.login("main", fields=fields)
except KeyError as e:
    st.error(f"KeyError: {e}. Possible issue with the credentials dictionary or session state.")
    st.stop()

# Displaying messages based on authentication status
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.title("Simple Authenticated App")
    st.write("You are now logged in!")
elif authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password")

# Close the database connection
conn.close()
