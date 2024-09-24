import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import re
import bcrypt
import streamlit_authenticator as stauth

# Load the image
logo = Image.open("hf_logo.png")

# Display the image at the top of the app
st.image(logo, width=200)  # Adjust the width as needed

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
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.title("Order Evaluation")

    st.markdown("### 🔧 Settings")

    # Function to read and process Excel data
    @st.cache_data
    def read_excel_data(uploaded_file):
        sheets_dict = pd.read_excel(uploaded_file, sheet_name=None)
        combined_df = pd.DataFrame()
        for sheet_name, df in sheets_dict.items():
            df['Sheet'] = sheet_name
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        return sheets_dict, combined_df

    # Function to sanitize sheet names
    def sanitize_sheet_name(sheet_name):
        sanitized_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
        return sanitized_name[:31]  # Truncate to 31 characters

    # Upload the Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    # Reset the graph when a new file is uploaded
    if uploaded_file:
        st.session_state.plot = None  # Clear the previous plot

        sheets_dict, combined_df = read_excel_data(uploaded_file)
        columns = combined_df.columns.tolist()

        # Create selectboxes for column and cycle time
        selected_column = st.selectbox("Choose a column to plot", columns)
        cycle_time_column = st.selectbox("Choose the cycle time column", columns)

        # Checkbox to enable step number filtering
        process_step_number = st.checkbox("Process based on step number?")

        # Define a variable for grouping column, default to cycle time column
        group_by_column = cycle_time_column

        if process_step_number:
            # Show the step number selection fields if the checkbox is checked
            step_number_column = st.selectbox("Choose the step number column", columns)
            step_value = st.number_input("Enter the step number value", min_value=0, value=1, step=1)

            # Convert the step number column to numeric if it's not already
            try:
                combined_df[step_number_column] = pd.to_numeric(combined_df[step_number_column], errors='coerce')
            except Exception as e:
                st.error(f"Error converting {step_number_column} to numeric: {e}")
                st.stop()

            # Filter the data based on the selected step number
            filtered_df = combined_df[combined_df[step_number_column] >= step_value + 1].dropna()

            # Ensure valid data exists before setting 'New Cycle Time'
            if not filtered_df.empty:
                # Set the group_by_column to 'New Cycle Time' if processing step number
                filtered_df['New Cycle Time'] = filtered_df.groupby('Sheet').cumcount() + 1
                group_by_column = 'New Cycle Time'

                # Button to preview the filtered dataset
                if st.button('Preview Filtered Data'):
                    st.markdown("### Preview of Filtered Dataset with New Cycle Time Column")
                    st.dataframe(filtered_df)
            else:
                st.warning("No data available after step number filtering.")
        else:
            # If the user doesn't want to process step number, use the entire dataset
            filtered_df = combined_df.copy()

        # Button to show data as a table
        if st.button('Show Data'):
            selected_data = pd.DataFrame()

            for sheet_name, df in sheets_dict.items():
                if selected_column in df.columns:
                    sanitized_sheet_name = sanitize_sheet_name(sheet_name)
                    if process_step_number and step_number_column in df.columns:
                        selected_data[sanitized_sheet_name] = df[df[step_number_column] >= step_value + 1][selected_column]
                    else:
                        selected_data[sanitized_sheet_name] = df[selected_column]

            # Drop rows with None values in the selected column
            selected_data = selected_data.dropna()

            # Check if selected data is available
            if not selected_data.empty:
                # Calculate mean and ±1 standard deviation grouped by the group_by_column
                cleaned_df = filtered_df[[selected_column, group_by_column]].dropna()
                grouped = cleaned_df.groupby(group_by_column)
                mean_values = grouped.mean().reset_index()
                std_values = grouped.std().reset_index()

                selected_data['Mean'] = mean_values[selected_column]
                selected_data['+1 Std Dev'] = mean_values[selected_column] + std_values[selected_column]
                selected_data['-1 Std Dev'] = mean_values[selected_column] - std_values[selected_column]

                # Store the selected data in session state and display it
                st.session_state.selected_data = selected_data
                st.dataframe(selected_data)
            else:
                st.warning("No data available for the selected column.")

        # Button to show the graph
        if st.button('Show Graph'):
            # Ensure selected columns exist and have valid data
            if selected_column in filtered_df.columns and group_by_column in filtered_df.columns:
                cleaned_df = filtered_df[[selected_column, group_by_column]].dropna()

                # Check if the data has enough rows to plot
                if not cleaned_df.empty:
                    # Group by group_by_column and calculate statistics
                    grouped = cleaned_df.groupby(group_by_column)
                    mean_values = grouped.mean().reset_index()
                    median_values = grouped.median().reset_index()
                    std_values = grouped.std().reset_index()

                    # Create a Plotly figure
                    fig = go.Figure()

                    # Add data trace for each sheet
                    for sheet_name, df in sheets_dict.items():
                        if process_step_number:
                            filtered_sheet_df = df[df[step_number_column] >= step_value + 1].dropna(subset=[selected_column, cycle_time_column])
                            # Add 'New Cycle Time' only if process_step_number is active and data is valid
                            if not filtered_sheet_df.empty:
                                filtered_sheet_df['New Cycle Time'] = filtered_sheet_df.groupby('Sheet').cumcount() + 1
                        else:
                            filtered_sheet_df = df.dropna(subset=[selected_column, cycle_time_column])

                        if not filtered_sheet_df.empty:
                            fig.add_trace(go.Scatter(x=filtered_sheet_df[group_by_column], y=filtered_sheet_df[selected_column], mode='lines', line=dict(color='blue'), showlegend=False))

                    # Add mean, median, and std deviation lines
                    fig.add_trace(go.Scatter(x=mean_values[group_by_column], y=mean_values[selected_column], mode='lines', name='Overall mean', line=dict(color='red', dash='dash')))
                    fig.add_trace(go.Scatter(x=median_values[group_by_column], y=median_values[selected_column], mode='lines', name='Overall median', line=dict(color='green', dash='dot')))
                    fig.add_trace(go.Scatter(x=std_values[group_by_column], y=mean_values[selected_column] + std_values[selected_column], mode='lines', name='Overall +1 std dev', line=dict(color='orange', dash='dashdot')))
                    fig.add_trace(go.Scatter(x=std_values[group_by_column], y=mean_values[selected_column] - std_values[selected_column], mode='lines', name='Overall -1 std dev', line=dict(color='orange', dash='dashdot')))

                    # Update plot layout
                    fig.update_layout(
                        title=f'<b>Line Chart of {selected_column}</b> across all sheets',
                        xaxis_title=group_by_column,
                        yaxis_title=selected_column,
                        title_font=dict(size=18, color='navy'),
                        autosize=True,
                        width=900,
                        height=700,
                        font=dict(size=16)
                    )

                    # Store the plot in session state
                    st.session_state.plot = fig

                else:
                    st.error("No data available for the selected column.")
            else:
                st.error("Invalid column selection for plotting.")

        # Display the graph if available
        if 'plot' in st.session_state and st.session_state.plot:
            st.plotly_chart(st.session_state.plot, use_container_width=True)

elif authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your username and password")
