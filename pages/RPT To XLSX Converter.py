import streamlit as st
import pandas as pd
import bcrypt
import streamlit_authenticator as stauth
from io import BytesIO


# Authentication Section
if 'authenticator' not in st.session_state:
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

    # Initialize the authenticator and store it in session state
    st.session_state['authenticator'] = stauth.Authenticate(
        credentials,
        "some_cookie_name",  # Replace with actual cookie name
        "some_signature_key",  # Replace with actual signature key
        cookie_expiry_days=3
    )

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


def read_rpt_file(file):
    """
    Function to read a .rpt file and convert it to a DataFrame.
    Assumes the .rpt file uses ';' as the delimiter.
    """
    lines = []
    try:
        # Attempt to read with ISO-8859-1 encoding (handles `\xb0`)
        lines = file.readlines()
        lines = [line.decode('ISO-8859-1').strip() for line in lines]
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame(), ""

    # Check if the file has enough lines
    if len(lines) < 2:
        st.error("The .rpt file does not contain enough data to process.")
        return pd.DataFrame(), ""

    # First row (metadata)
    first_row = lines[0]

    # Header row
    header = lines[1].split(';')

    # Make header unique
    def make_unique(header):
        counts = {}
        new_header = []
        for name in header:
            if name in counts:
                counts[name] += 1
                new_name = f"{name}_{counts[name]}"
            else:
                counts[name] = 0
                new_name = name
            new_header.append(new_name)
        return new_header

    header = make_unique(header)

    # Data rows
    data = []
    for line in lines[2:]:
        row = line.split(';')
        if len(row) == len(header):
            data.append(row)

    # Check if data is empty
    if not data:
        st.warning("The .rpt file does not contain any data rows after the header.")
        return pd.DataFrame(columns=header), first_row

    # Create a DataFrame
    df = pd.DataFrame(data, columns=header)

    # Convert numeric columns to appropriate data types
    df = df.apply(pd.to_numeric, errors='ignore')

    return df, first_row

def save_as_excel(dataframes, first_rows):
    """
    Function to save multiple DataFrames as separate sheets in an Excel file
    and return the content as a BytesIO object.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for i, (df, first_row) in enumerate(zip(dataframes, first_rows)):
            sheet_name = f'Sheet{i+1}'
            df.to_excel(writer, sheet_name=sheet_name, startrow=0, index=False)
            worksheet = writer.sheets[sheet_name]
    output.seek(0)
    return output

def save_first_rows_to_text(first_rows):
    """
    Function to save the first rows of all .rpt files into a text file
    and return the content as a BytesIO object.
    """
    output = BytesIO()
    for i, first_row in enumerate(first_rows):
        output.write(f"First row from file {i+1}:\n".encode('utf-8'))
        output.write((first_row + "\n\n").encode('utf-8'))
    output.seek(0)
    return output


if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")

    # Streamlit app
    st.title("RPT to XLSX Converter")

    # File uploader
    uploaded_files = st.file_uploader("Upload .rpt files", type="rpt", accept_multiple_files=True)

    if uploaded_files:
        dataframes = []
        first_rows = []
        for uploaded_file in uploaded_files:
            # Read the .rpt file
            df, first_row = read_rpt_file(uploaded_file)
            dataframes.append(df)
            first_rows.append(first_row)
        
        # Display the DataFrames
        for i, df in enumerate(dataframes):
            st.write(f"DataFrame from {uploaded_files[i].name}")
            st.dataframe(df)
        
        # Input for the Excel file name
        excel_filename = st.text_input("Enter the Excel file name", "output.xlsx")
        
        # Input for the Text file name
        text_filename = st.text_input("Enter the text file name for information text file", "Info.txt")
        
        # Button to save as Excel and provide download link
        #if st.button("Save and Download Excel & Text Files"):
            # Save Excel file to memory and provide download link
        excel_data = save_as_excel(dataframes, first_rows)
        # Save first rows as a text file to memory and provide download link
        text_data = save_first_rows_to_text(first_rows)
                                                
        st.download_button(
            label="Download Excel file",
            data=excel_data,
            file_name=excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
                
            
        st.download_button(
            label="Download Text file",
            data=text_data,
            file_name=text_filename,
            mime="text/plain"
            )

elif authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your username and password")
