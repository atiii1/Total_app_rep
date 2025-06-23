import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import streamlit_authenticator as stauth
import bcrypt
from io import BytesIO

# Load logo
logo = Image.open("hf_logo.png")
st.image(logo, width=200)

# Authenticator setup
if 'authenticator' not in st.session_state:
    st.session_state.authenticator = None

names = ["Admin User"]
usernames = ["admin"]
passwords = ["hbfb"]
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

fields = {
    "Form name": "Login",
    "Username": "Username",
    "Password": "Password",
    "Login": "Login"
}

name, authentication_status, username = authenticator.login("main", fields=fields)

def main():
    st.title("Ram Position Analysis")

    uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)
        first_sheet = pd.read_excel(xls, sheet_name=xls.sheet_names[0])

        numeric_columns = first_sheet.select_dtypes(include=np.number).columns.tolist()
        if not numeric_columns:
            st.error("The first sheet does not contain numeric columns.")
            return

        ram_col = st.selectbox("Select Ram Position column", numeric_columns)
        cycle_col = st.selectbox("Select Cycle Time column", numeric_columns)

        threshold_value = st.number_input("Enter the Ram HIGH threshold value:", min_value=0.0, step=1.0, value=300.0)
        low_threshold_value = st.number_input("Enter the Ram LOW threshold value:", min_value=0.0, step=1.0, value=0.0)

        # ---------- CALCULATION ----------
        if st.button("Start Calculation"):
            all_results = []
            for sheet in xls.sheet_names:
                try:
                    df = pd.read_excel(xls, sheet_name=sheet)
                    if ram_col not in df.columns or cycle_col not in df.columns:
                        continue

                    ram_values = df[ram_col].values
                    cycle_time_values = df[cycle_col].values

                    zero_crossings = []
                    start_time = None
                    tracking = False

                    for i in range(1, len(ram_values)):
                        if not tracking and ram_values[i - 1] >= threshold_value and ram_values[i] < threshold_value:
                            start_time = cycle_time_values[i]
                            tracking = True

                        if tracking and ram_values[i] <= low_threshold_value:
                            end_time = cycle_time_values[i]
                            delta_time = end_time - start_time
                            zero_crossings.append((start_time, end_time, delta_time))
                            tracking = False

                    if zero_crossings:
                        result_df = pd.DataFrame(zero_crossings, columns=["Start Time", "End Time", "Delta Time"])
                        result_df["Sheet"] = sheet
                        all_results.append(result_df)
                except Exception as e:
                    st.warning(f"Error processing sheet '{sheet}': {e}")

            if not all_results:
                st.warning("No valid transitions found with the selected thresholds.")
            else:
                combined_df = pd.concat(all_results, ignore_index=True)
                st.subheader("Combined Delta Time Results")
                st.write(combined_df)

                # Generate downloadable Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    combined_df.to_excel(writer, index=False, sheet_name='Delta Times')

                st.download_button(
                    label="Download Results as Excel",
                    data=output.getvalue(),
                    file_name="delta_time_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # ---------- GRAPH PREVIEW ----------
        selected_sheet = st.selectbox("Select a sheet to preview graph", xls.sheet_names)

        if st.button("Preview Graph"):
            try:
                df_plot = pd.read_excel(xls, sheet_name=selected_sheet)
                if ram_col not in df_plot.columns or cycle_col not in df_plot.columns:
                    st.warning("Selected columns not found in the chosen sheet.")
                    return

                ram_values = df_plot[ram_col].values
                cycle_time_values = df_plot[cycle_col].values

                # Recalculate transitions for preview
                zero_crossings = []
                start_time = None
                tracking = False

                for i in range(1, len(ram_values)):
                    if not tracking and ram_values[i - 1] >= threshold_value and ram_values[i] < threshold_value:
                        start_time = cycle_time_values[i]
                        tracking = True

                    if tracking and ram_values[i] <= low_threshold_value:
                        end_time = cycle_time_values[i]
                        delta_time = end_time - start_time
                        zero_crossings.append((start_time, end_time, delta_time))
                        tracking = False

                result_df = pd.DataFrame(zero_crossings, columns=["Start Time", "End Time", "Delta Time"])

                # Plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=cycle_time_values, y=ram_values,
                                         mode="lines", name="Ram Position", line=dict(color="blue")))

                for start, end, _ in result_df.values:
                    fig.add_vrect(x0=start, x1=end, fillcolor="red", opacity=0.3, layer="below", line_width=0)

                fig.update_layout(
                    title=f"Ram Position with Delta Times – Sheet: {selected_sheet}",
                    xaxis_title="Cycle Time",
                    yaxis_title="Ram Position",
                    hovermode="x"
                )
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error generating graph: {e}")

# Login control
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    if __name__ == "__main__":
        main()

elif authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password")
