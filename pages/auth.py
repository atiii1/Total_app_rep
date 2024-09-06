import streamlit as st
import bcrypt
import streamlit_authenticator as stauth

# Clear session state to avoid referencing old credentials
if 'authenticator' not in st.session_state:
    st.session_state['authenticator'] = None

# Define user credentials
names = ["Admin User"]
usernames = ["admin"]
passwords = ["hbfb"]

# Hash passwords using bcrypt
hashed_passwords = [bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() for password in passwords]

# Create a dictionary for credentials
credentials = {
    "usernames": {
        "admin": {"name": "Admin User", "password": hashed_passwords[0]},
    }
}

# Initialize the authenticator
if st.session_state['authenticator'] is None:
    authenticator = stauth.Authenticate(
        credentials,
        "some_cookie_name",
        "some_signature_key",
        cookie_expiry_days=3
    )
    st.session_state['authenticator'] = authenticator
else:
    authenticator = st.session_state['authenticator']

# Custom fields for login
fields = {
    "Form name": "Login",
    "Username": "Username",
    "Password": "Password",
    "Login": "Login"
}

# Login widget with fields parameter
name, authentication_status, username = authenticator.login("main", fields=fields)

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
