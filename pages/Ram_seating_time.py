import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import streamlit_authenticator as stauth
import bcrypt

# Load the image
logo = Image.open("hf_logo.png")

# Display the image at the top of the app
st.image(logo, width=200)  # Adjust the width as needed

# Initialize session state for the authenticator if not already done
if 'authenticator' not in st.session_state:
    st.session_state.authenticator = None

# Define user credentials with email
names = ["Admin User"]
usernames = ["admin"]
passwords = ["hbfb"]

# Hash passwords using bcrypt
hashed_passwords = [bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() for password in passwords]

# Add email to the credentials
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": hashed_passwords[0],
            "email": "atefehnafari1993@gmail.com"  # Add this line for email
        }
    }
}

# Initialize the authenticator if not already in session state
if st.session_state.authenticator is None:
    authenticator = stauth.Authenticate(
        credentials,
        "some_cookie_name",
        "some_signature_key",
        cookie_expiry_days=3
    )
    st.session_state.authenticator = authenticator
else:
    authenticator = st.session_state.authenticator

# Custom fields for login
fields = {
    "Form name": "Login",
    "Username": "Username",
    "Password": "Password",
    "Login": "Login"
}
# Perform login using authenticator
name, authentication_status, username = authenticator.login("main", fields=fields)
def main():
    # Streamlit UI
    st.title("Ram Position Analysis")

    # Use session state to store the uploaded file and selections
    if "uploaded_df" not in st.session_state:
        st.session_state.uploaded_df = None
    if "selected_sheet" not in st.session_state:
        st.session_state.selected_sheet = None
    if "df" not in st.session_state:
        st.session_state.df = None

    # File uploader
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

    if uploaded_file:
        # Load Excel file once
        if st.session_state.uploaded_df is None:
            st.session_state.uploaded_df = pd.ExcelFile(uploaded_file)

        xls = st.session_state.uploaded_df

        # Select sheet (avoid reloading)
        sheet_name = st.selectbox("Select a sheet", xls.sheet_names, index=0)

        if sheet_name != st.session_state.selected_sheet:
            st.session_state.selected_sheet = sheet_name
            st.session_state.df = pd.read_excel(xls, sheet_name=sheet_name)

        df = st.session_state.df
        st.write("Preview of uploaded data:", df.head())

        # Column selection
        ram_position_col = st.selectbox("Select the Ram Position column", df.columns, key="ram_col")
        cycle_time_col = st.selectbox("Select the Cycle Time column", df.columns, key="cycle_col")

        # Ensure column selection is stored
        st.session_state.ram_position_col = ram_position_col
        st.session_state.cycle_time_col = cycle_time_col

        # Button to display graph
        if st.button("View Graph"):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df[cycle_time_col], y=df[ram_position_col], 
                                    mode="lines", name="Ram Position", line=dict(color="blue")))
            fig.update_layout(
                title="Ram Position over Cycle Time",
                xaxis_title="Cycle Time",
                yaxis_title="Ram Position",
                hovermode="x",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Delta Time Calculation
        st.subheader("Delta Time Calculation")

        if st.button("Calculate Delta Time"):
            # Retrieve the correct selected columns
            ram_position_col = st.session_state.ram_position_col
            cycle_time_col = st.session_state.cycle_time_col

            # Ensure the DataFrame is still accessible
            if st.session_state.df is not None:
                df = st.session_state.df
                ram_values = df[ram_position_col].values
                cycle_time_values = df[cycle_time_col].values

                zero_crossings = []
                start_time = None
                tracking = False  # Flag to track when we find a valid start point

                for i in range(1, len(ram_values)):
                    # Ensure we detect the FIRST falling edge after being above 300
                    if not tracking and ram_values[i - 1] >= 300 and ram_values[i] < 300:
                        start_time = cycle_time_values[i]
                        tracking = True  # Start tracking for zero crossing
                    
                    # Ensure we correctly find the zero crossing AFTER the falling edge
                    if tracking and ram_values[i] == 0:
                        end_time = cycle_time_values[i]
                        delta_time = end_time - start_time
                        zero_crossings.append((start_time, end_time, delta_time))
                        tracking = False  # Reset tracking for next fall

                # Display results
                if zero_crossings:
                    result_df = pd.DataFrame(zero_crossings, columns=["Start Time", "End Time", "Delta Time"])
                    st.write("Delta Time Calculations:", result_df)

                    # Plot interactive graph with highlighted regions
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=cycle_time_values, y=ram_values, 
                                            mode="lines", name="Ram Position", line=dict(color="blue")))

                    for start, end, _ in zero_crossings:
                        fig.add_vrect(x0=start, x1=end, fillcolor="red", opacity=0.3, layer="below", line_width=0)

                    fig.update_layout(
                        title="Ram Position with Highlighted Delta Times",
                        xaxis_title="Cycle Time",
                        yaxis_title="Ram Position",
                        hovermode="x",
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No valid transitions found where the value drops below 300 and reaches zero.")
            else:
                st.write("Error: No data available. Please re-upload the file.")


# Check if the user has successfully logged in
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")

    if __name__ == "__main__":
        main()

# If login fails, show the appropriate error or warning message
elif authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your username and password")
