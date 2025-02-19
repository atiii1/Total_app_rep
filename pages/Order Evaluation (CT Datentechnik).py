#this is test code to update  excel file analysis#
####################################################
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import re
import bcrypt
import streamlit_authenticator as stauth
import io

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

# Check if the user has successfully logged in
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.title("Order Evaluation (CT Datentechnik)")

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
        st.session_state.plot_selected = None  # Clear the mean graph as well
        #st.session_state.download_completed = False # clear flag of downloaded data

        sheets_dict, combined_df = read_excel_data(uploaded_file)
        columns = combined_df.columns.tolist()

        # Create selectboxes for column and cycle time
        selected_column = st.selectbox("Choose a column to plot", columns)
        cycle_time_column = st.selectbox("Choose the cycle time column", columns)
         # Define a variable for grouping column, default to cycle time column
        group_by_column = cycle_time_column

        

        # Radio button for processing type
        process_type = st.radio("Choose processing type:", ["Process with Step Number", "Process without Step Number"])

        # Function to filter sheets with step number
        @st.cache_data
        def filter_sheets_with_step(sheets, column, value):
            filtered = {}
            for sheet_name, df in sheets.items():
                if column in df.columns:
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                    filtered_df = df[df[column] >= value + 1].dropna()
                    if not filtered_df.empty:
                        filtered_df['New Cycle Time'] = filtered_df.groupby('Sheet').cumcount() + 1
                        filtered[sheet_name] = filtered_df
            return filtered
        
        # Add a separator line
        st.divider()

        if process_type == "Process with Step Number":
            st.markdown("### 📊Processing with Step Number")
            # Step number selection fields
            step_number_column = st.selectbox("Choose the step number column", columns)
            step_value = st.number_input("Enter the step number value", min_value=0, value=1, step=1)

            # Function to filter data per sheet (with caching for performance)
            @st.cache_data
            def filter_sheets(sheets, column, value):
                filtered = {}
                for sheet_name, df in sheets.items():
                    if column in df.columns:
                        # Convert column to numeric and apply the filter
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                        filtered_df = df[df[column] >= value + 1].dropna()

                        # Add 'New Cycle Time' if the DataFrame is not empty
                        if not filtered_df.empty:
                            filtered_df['New Cycle Time'] = filtered_df.groupby('Sheet').cumcount() + 1
                            filtered[sheet_name] = filtered_df
                return filtered

            # Filter sheets
            filtered_sheets = filter_sheets(sheets_dict, step_number_column, step_value)

            if filtered_sheets:

                # Display the graph after processing
                if st.button('Show graph of filtered Data'):

                    st.markdown("### 📈Filtered Data Visualization")
                    fig_filtered = go.Figure()

                    # Combine all filtered data into one DataFrame
                    combined_filtered_df = pd.concat(filtered_sheets.values(), ignore_index=True)

                    if not combined_filtered_df.empty:
                        # Ensure necessary columns are numeric
                        combined_filtered_df['New Cycle Time'] = pd.to_numeric(combined_filtered_df['New Cycle Time'], errors='coerce')
                        combined_filtered_df[selected_column] = pd.to_numeric(combined_filtered_df[selected_column], errors='coerce')

                        # Drop rows with NaN values in the required columns
                        combined_filtered_df = combined_filtered_df.dropna(subset=['New Cycle Time', selected_column])

                        # Calculate overall statistics grouped by 'New Cycle Time'
                        grouped = combined_filtered_df.groupby('New Cycle Time')
                        overall_mean = grouped[selected_column].mean().reset_index()
                        overall_median = grouped[selected_column].median().reset_index()
                        overall_std = grouped[selected_column].std().reset_index()

                        # Plot each individual sheet's filtered data
                        for sheet_name, filtered_df in filtered_sheets.items():
                            fig_filtered.add_trace(go.Scatter(
                                x=filtered_df['New Cycle Time'],
                                y=filtered_df[selected_column],
                                mode='lines',
                                line=dict(color='blue'),
                                showlegend=False,
                                name=f'{sheet_name} Filtered'
                            ))

                        # Add overall mean trace
                        fig_filtered.add_trace(go.Scatter(
                            x=overall_mean['New Cycle Time'],
                            y=overall_mean[selected_column],
                            mode='lines',
                            line=dict(color='red', dash='dash'),
                            name='Overall Mean'
                        ))

                        # Add overall median trace
                        fig_filtered.add_trace(go.Scatter(
                            x=overall_median['New Cycle Time'],
                            y=overall_median[selected_column],
                            mode='lines',
                            line=dict(color='green', dash='dot'),
                            name='Overall Median'
                        ))

                        # Add overall standard deviation traces
                        fig_filtered.add_trace(go.Scatter(
                            x=overall_std['New Cycle Time'],
                            y=overall_mean[selected_column] + overall_std[selected_column],
                            mode='lines',
                            line=dict(color='orange', dash='dashdot'),
                            name='Overall +1 Std Dev'
                        ))
                        fig_filtered.add_trace(go.Scatter(
                            x=overall_std['New Cycle Time'],
                            y=overall_mean[selected_column] - overall_std[selected_column],
                            mode='lines',
                            line=dict(color='orange', dash='dashdot'),
                            name='Overall -1 Std Dev'
                        ))

                        # Update the layout of the figure
                        fig_filtered.update_layout(
                            title=f'<b>Line Chart of Filtered {selected_column}</b>',
                            xaxis_title="New Cycle Time",
                            yaxis_title=selected_column,
                            title_font=dict(size=18, color='navy'),
                            autosize=True,
                            width=900,
                            height=700,
                        )
                        st.plotly_chart(fig_filtered, use_container_width=True)

                    else:
                        st.warning("No valid data available for plotting. Please check your filter conditions.")
                # Get the current page name 
                # Unique identifier for the current page
                # Unique identifier for the current page
                page_name = "page_1"  # Replace with a unique identifier for each page

                # Unique keys for session state variables
                downloaded_key = f"download_completed_{page_name}"

                # Initialize session state variables for this page if not already set
                if downloaded_key not in st.session_state:
                    st.session_state[downloaded_key] = False

                # Display the question and buttons in a single column
                st.write("If you want to download the filtered data-set as an Excel file,preess button of 'Prepare data to download'.")
                yes_button = st.button("Prepare data to download", key=f"yes_button_{page_name}")
                #no_button = st.button("No", key=f"no_button_{page_name}")

                # Handle button actions
                if yes_button and not st.session_state[downloaded_key]:
                    # Simulate the download process
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for sheet_name, filtered_df in filtered_sheets.items():
                            filtered_df.to_excel(writer, index=False, sheet_name=sheet_name[:31])  # Truncate sheet name if needed
                        writer.close()

                    # Provide the download button
                    st.download_button(
                        label="Download All Filtered Data as Excel",
                        data=output.getvalue(),
                        file_name="filtered_data_all_sheets.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    # Mark the dataset as downloaded
                    st.session_state[downloaded_key] = True
                
                elif st.session_state[downloaded_key]:
                    st.success("Data has already been downloaded. Reload the page to download again.")

            else:
                st.warning("No data available after filtering. Please check your filter conditions.")


        elif process_type == "Process without Step Number":
            st.markdown("### 📊Processing without Step Number")
            # Initialize filtered_df
            filtered_df = combined_df.copy()


            if st.button('Show Data'):
                # Initialize a dictionary to collect column data
                
                data_columns = {}

                for sheet_name, df in sheets_dict.items():
                    if selected_column in df.columns:
                        sanitized_sheet_name = sanitize_sheet_name(sheet_name)
                        # Set a unique identifier (or reset index if no identifier exists)
                        df = df.reset_index()  # Adjust this based on actual unique identifiers
                        # Add the column data to the dictionary
                        data_columns[sanitized_sheet_name] = pd.to_numeric(df[selected_column], errors='coerce')

                # Create a DataFrame from the collected columns, aligning by index
                result_table = pd.DataFrame(data_columns)

                # Add Mean, Median, and Std Dev columns
                result_table['Mean'] = result_table.mean(axis=1, skipna=True)
                result_table['Median'] = result_table.median(axis=1, skipna=True)
                result_table['Std Dev'] = result_table.std(axis=1, skipna=True)

                # Display the table
                st.markdown("### 📋 Combined Table of Selected Data with Statistics")
                st.dataframe(result_table)

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
            
        # Add a separator line
        st.divider()

        #mean graphs of selecting variables
        # Mean Graphs Setting section
       # Mean Graphs Setting section
        st.markdown("### 📈Mean Graphs Setting")
        
        if cycle_time_column:
            st.warning(f'Cycle Time is selected: {cycle_time_column}')
            # User input for the number of fields
            num_fields = st.slider("How many fields do you want to analyze?", min_value=1, max_value=7, value=1)

            selected_columns = []
            for i in range(num_fields):
                selected_columns.append(st.selectbox(f"Choose Parameter {i+1}", columns, key=f"col_{i}"))

            # Button to show the graph for selected variables
            if st.button('Show Graph for Selected Variables'):
                if len(selected_columns) != len(set(selected_columns)):
                    st.error("Please select unique parameters for all fields.")
                else:
                    # Ensure all columns have the same length by dropping rows with NaNs
                    combined_selection = [cycle_time_column] + selected_columns
                    cleaned_df = combined_df[combined_selection].dropna(subset=combined_selection)

                    # Convert necessary columns to numeric
                    for col in combined_selection:
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

                    # Group by cycle time and calculate mean values
                    grouped = cleaned_df.groupby(cycle_time_column).mean().reset_index()

                    # Determine the range for each selected column
                    column_ranges = {column: (grouped[column].max() - grouped[column].min()) for column in selected_columns}

                    # Sort columns by range in descending order
                    sorted_columns = sorted(column_ranges, key=column_ranges.get, reverse=True)

                    # Create a Plotly figure for selected variables
                    fig_selected = go.Figure()

                    # Add traces for each selected column
                    for i, column in enumerate(sorted_columns):
                        axis = 'y1' if i == 0 else 'y2'
                        fig_selected.add_trace(go.Scatter(
                            x=grouped[cycle_time_column],
                            y=grouped[column],
                            mode='lines',
                            name=f'Mean {column}',
                            yaxis=axis
                        ))

                    # Update layout for multiple y-axes
                    fig_selected.update_layout(
                        title=f'<b>Mean Values of Selected Parameters across all sheets</b>',
                        xaxis_title=cycle_time_column,
                        yaxis=dict(
                            title=sorted_columns[0],
                            titlefont=dict(color="blue"),
                            tickfont=dict(color="blue"),
                            side='left'
                        ),
                        yaxis2=dict(
                            title=sorted_columns[1] if len(sorted_columns) > 1 else "",
                            titlefont=dict(color="red"),
                            tickfont=dict(color="red"),
                            overlaying='y',
                            side='right'
                        ),
                        legend=dict(
                            x=1.05,
                            y=1,
                            traceorder="normal",
                            font=dict(size=12),
                        ),
                        title_font=dict(size=18, color='navy'),
                        autosize=True,
                        width=900,
                        height=700,
                        font=dict(size=16)
                    )

                    # Store the plot and grouped data in session state
                    st.session_state.plot_selected = fig_selected
                    st.session_state.grouped_data = grouped  # Save the grouped data for later use

            # Display the graph for selected variables if available
            if 'plot_selected' in st.session_state and isinstance(st.session_state.plot_selected, go.Figure) and st.session_state.plot_selected:
                st.plotly_chart(st.session_state.plot_selected, use_container_width=True)

            # Button to show the table of selected mean graph data
            if st.button('Show Table of Selected Data'):
                if 'grouped_data' in st.session_state and not st.session_state.grouped_data.empty:
                    # Display the grouped data in a table
                    st.markdown("### 📋 Table of Selected Data")
                    st.dataframe(st.session_state.grouped_data)
                else:
                    st.warning("No data is available to display. Please generate the graph first.")

        else:
            st.warning("Cycle time is not selected.")
        
    else:
        st.warning('No file is uploaded.')      
# If login fails, show the appropriate error or warning message
elif authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your username and password")
