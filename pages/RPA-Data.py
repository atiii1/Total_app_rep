import pandas as pd
import streamlit as st
import chardet
import tempfile
from PIL import Image
import streamlit_authenticator as stauth
import bcrypt
import zipfile
import os
import re

# --- Branding ---
try:
    logo = Image.open("hf_logo.png")
    st.image(logo, width=200)
except Exception:
    st.write("")

# --- Authenticator session init ---
if 'authenticator' not in st.session_state:
    st.session_state.authenticator = None

# --- Credentials (demo) ---
names = ["Admin User"]
usernames = ["admin"]
passwords = ["hbfb"]

# Hash passwords using bcrypt
hashed_passwords = [bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() for password in passwords]

credentials = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": hashed_passwords[0],
            "email": "atefehnafari1993@gmail.com"
        }
    }
}

# --- Authenticator init (persist in session) ---
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

# --- Custom login form labels ---
fields = {
    "Form name": "Login",
    "Username": "Username",
    "Password": "Password",
    "Login": "Login"
}

# --- Login ---
name, authentication_status, username = authenticator.login("main", fields=fields)

def sanitize_filename(s: str, fallback: str) -> str:
    """Remove/replace characters invalid for filenames, return fallback if empty."""
    if not s:
        return fallback
    # Trim and replace invalid filename chars
    s = s.strip()
    s = re.sub(r'[\\/:*?"<>|]+', '_', s)  # Windows-invalid + common bad chars
    s = s.strip(' .')  # avoid trailing dots/spaces
    return s or fallback

def main():
    st.title("CSV to XLSX Converter")

    # Choose what line 3 contains
    key_choice = st.selectbox(
        "What does line 3 contain?",
        ("Order", "Lot"),
        index=0,
        help="Select 'Order' if line 3 looks like '...Order;XYZ'. Select 'Lot' if it looks like '...Lot;ABC'."
    )


    # Upload input (multiple files)
    uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

    # Keep track of converted temp paths to zip later
    converted_files = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()

            # Detect encoding
            detected = chardet.detect(file_bytes)
            encoding = detected.get('encoding')

            if not encoding:
                st.error(f"Could not detect file encoding for {uploaded_file.name}. Please check the file format.")
                continue

            try:
                # Decode and split into lines
                text = file_bytes.decode(encoding)
                lines = text.splitlines()

                METADATA_LINES = 14
                HEADER_INDEX = 14
                DATA_START_INDEX = 15

                # Guard against too-short files
                if len(lines) < 3:
                    st.error(f"File **{uploaded_file.name}** is too short to contain line 3.")
                    continue

                # Determine which keyword to expect on line 3
                line3 = lines[2]
                expected_key = f"{key_choice};"  # "Order;" or "Lot;"
                if expected_key not in line3:
                    st.error(
                        f"**{uploaded_file.name}**: Expected to find '{expected_key}' on line 3, "
                        f"but line 3 was: `{line3}`"
                    )
                    continue

                # Extract the value after the chosen keyword
                extracted_value = line3.split(expected_key, 1)[1].strip()
                base_name = sanitize_filename(
                    extracted_value,
                    fallback=os.path.splitext(uploaded_file.name)[0]
                )
                base_xlsx_name = f"{base_name}.xlsx"

                st.write(f"Processing **{uploaded_file.name}**")
                st.write(f"Detected `{key_choice}` value on line 3 → **{base_name}**")

                # Now guard header presence
                if len(lines) <= HEADER_INDEX:
                    st.error(f"**{uploaded_file.name}** is too short to contain a header at line {HEADER_INDEX+1}.")
                    continue

                # Split parts
                metadata = lines[:METADATA_LINES]
                header_row = lines[HEADER_INDEX].split(";")
                data_table = lines[DATA_START_INDEX:]

                # Write only the data rows into a temp CSV, then read with pandas
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as tmp_csv:
                    tmp_csv.write("\n".join(data_table))
                    tmp_csv_path = tmp_csv.name

                # Read data; header assigned after read (since we wrote raw data rows)
                df = pd.read_csv(
                    tmp_csv_path,
                    delimiter=";",
                    encoding=encoding,
                    decimal=",",
                    header=None
                )

                # Apply header row
                df.columns = header_row

                if df.empty:
                    st.error(f"No data found in the data table for **{uploaded_file.name}**.")
                    continue

                # Build combined dataframe (metadata + blank + header + data)
                num_cols = len(df.columns)
                expanded_metadata = [[line] + [""] * (num_cols - 1) for line in metadata]
                metadata_df = pd.DataFrame(expanded_metadata, columns=df.columns)
                blank_row = pd.DataFrame([[""] * num_cols], columns=df.columns)
                header_df = pd.DataFrame([header_row], columns=df.columns)

                combined_df = pd.concat([metadata_df, blank_row, header_df, df], ignore_index=True)

                # Save to temp xlsx
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_xlsx:
                    xlsx_path = tmp_xlsx.name

                with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
                    combined_df.to_excel(writer, sheet_name="Combined", index=False, header=False)

                converted_files.append((base_xlsx_name, xlsx_path))
                st.success(f"File **{uploaded_file.name}** processed successfully!")

            except Exception as e:
                st.error(f"An error occurred while processing {uploaded_file.name}: {e}")

        # Zip all converted files
        if converted_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
                zip_path = tmp_zip.name
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_name, file_path in converted_files:
                        zipf.write(file_path, os.path.basename(file_name))

            st.success("All files processed successfully!")
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Download All as ZIP",
                    data=f,
                    file_name="converted_files.zip",
                    mime="application/zip"
                )

# --- App body depending on auth state ---
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    if __name__ == "__main__":
        main()
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
