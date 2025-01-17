import pandas as pd
import streamlit as st
import chardet
import tempfile
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
    st.title("CSV to XLSX Converter")

    # File upload field
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        # Read the file's content as bytes
        file_content = uploaded_file.read()

        # Detect the encoding
        detected_encoding = chardet.detect(file_content)
        encoding = detected_encoding['encoding']

        if not encoding:
            st.error("Could not detect file encoding. Please check the file format.")
            return

        try:
            # Decode the file content with the detected encoding
            file_text = file_content.decode(encoding)
            lines = file_text.splitlines()

            # Extract the name after "Order;"
            if len(lines) >= 3 and "Order;" in lines[2]:
                order_name = lines[2].split("Order;")[1].strip()
                st.write(f"Extracted name for XLSX file: {order_name}")

                # Separate metadata and data
                metadata = lines[:14]  # First 14 lines as metadata
                header_row = lines[14].split(";")  # Header row for the data table
                data_table = lines[15:]  # Data starts from line 16

                # Write the data table to a temporary file
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as temp_file:
                    # Write the data table to the temp file
                    temp_file.write("\n".join(data_table))
                    temp_file_path = temp_file.name

                # Read the data table
                df = pd.read_csv(
                    temp_file_path,
                    delimiter=";",      # Handle semicolon-separated values
                    encoding=encoding,  # Use detected encoding
                    decimal=",",        # Interpret commas as decimal separators
                    header=None         # Do not assume any row as a header
                )

                # Set the header row explicitly
                df.columns = header_row

                # Handle case where no data exists
                if df.empty:
                    st.error("No data found in the data table.")
                    return

                # Expand metadata to match the table's column structure
                num_columns = len(df.columns)  # Total columns in the data table
                expanded_metadata = [[line] + [""] * (num_columns - 1) for line in metadata]

                # Create metadata DataFrame
                metadata_df = pd.DataFrame(expanded_metadata, columns=df.columns)

                # Add a blank row (optional) to separate metadata and data
                blank_row = pd.DataFrame([[""] * num_columns], columns=df.columns)

                # Create a DataFrame for the header row
                header_df = pd.DataFrame([header_row], columns=df.columns)

                # Combine metadata, blank row, header row, and data table
                combined_df = pd.concat([metadata_df, blank_row, header_df, df], ignore_index=True)

                # Save the combined data to an XLSX file
                xlsx_file_name = f"{order_name}.xlsx"
                with pd.ExcelWriter(xlsx_file_name, engine="openpyxl") as writer:
                    combined_df.to_excel(writer, sheet_name="Combined", index=False, header=False)

                # Provide the file for download
                st.success("File processed successfully!")
                with open(xlsx_file_name, "rb") as f:
                    st.download_button(
                        label="Download the processed file",
                        data=f,
                        file_name=xlsx_file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("The file does not contain the required 'Order;' text on line 3.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

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
