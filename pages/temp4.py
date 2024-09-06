import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to process uploaded file and detect intervals
def process_file(df, time_col, Power_col, Tc_col, Tm_col, active_Temp_col, tolerance, cooling_s):
    # Sorting by time column to ensure data is in chronological order
    df = df.sort_values(by=time_col).reset_index(drop=True)

    results = []
    start_index = 0
    while start_index < len(df):
        start_time = df[time_col].iloc[start_index]
        active_Temp_value = df[active_Temp_col].iloc[start_index]
        
        # Find the end of the phase where Active Temp is constant within the tolerance
        end_index = start_index
        while end_index < len(df) and abs(df[active_Temp_col].iloc[end_index] - active_Temp_value) <= tolerance:
            end_index += 1

        end_time = df[time_col].iloc[end_index - 1]
        duration = (end_time - start_time)

        if duration >= 10:
            # Calculate mean values during this interval
            interval_data = df.iloc[start_index:end_index]
            mean_Power = interval_data[Power_col].mean()
            mean_Tc = interval_data[Tc_col].mean()
            mean_Tm = interval_data[Tm_col].mean()
            alpha = mean_Power / (cooling_s * (mean_Tc - mean_Tm))
            results.append({
                'Active Temp': active_Temp_value,
                'interval_start': start_time,
                'interval_end': end_time,
                'Power values': interval_data[Power_col].tolist(),
                'mean of Power': mean_Power,
                'mean of Tc': mean_Tc,
                'mean of Tm': mean_Tm,
                'alpha': alpha
            })

        # Move to the next phase
        start_index = end_index

    return results

# Title of the app
st.title('Temperature Coefficient Calculation App')

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the uploaded file
    df = pd.read_excel(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df.head())

    # Drop the first row
    df = df.drop(0).reset_index(drop=True)

    # Column selection
    time_col = st.selectbox("Select the time column", df.columns)
    Power_col = st.selectbox("Select the Power column", df.columns)
    active_Temp_col = st.selectbox("Select the Active Temp column", df.columns)
    Compound_Temp_col = st.selectbox("Select the Compound Temp column", df.columns)
    Machine_Temp_col = st.selectbox("Select the Machine Temp column", df.columns)
    tolerance = st.number_input("Enter the tolerance for Active Temp", min_value=0.0, value=0.0)
    cooling_s = st.number_input("Enter the Cooling Surface", min_value=0.0, value=0.0)

    if st.button("Calculate"):
        results = process_file(df, time_col, Power_col, Compound_Temp_col, Machine_Temp_col, active_Temp_col, tolerance, cooling_s)

        if results:
            # Display the results
            st.write("Mean Value Calculation:")

            for result in results:
                st.write(f"Active Temp value: {result['Active Temp']}")
                st.write(f"Interval start: {result['interval_start']}")
                st.write(f"Interval end: {result['interval_end']}")
                st.write(f"Power values: {result['Power values']}")
                st.write(f"Mean Power value: {result['mean of Power']}")
                st.write(f"Mean Compound Temp: {result['mean of Tc']}")
                st.write(f"Mean Machine Temp: {result['mean of Tm']}")
                st.write(f"Alpha: {result['alpha']}")
                st.write(f"Cooling surface: {cooling_s}")

            # Convert results to DataFrame
            results_df = pd.DataFrame(results)

            # Display the results DataFrame for reference
            st.write("Summary of Intervals:")
            st.dataframe(results_df[['Active Temp', 'interval_start', 'interval_end', 'mean of Power', 'mean of Tc', 'mean of Tm', 'alpha']])

            # Plot Active Temp over time and highlight constant intervals
            plt.figure(figsize=(10, 6))
            plt.plot(df[time_col], df[active_Temp_col], label='Active Temp', color='blue')
            for result in results:
                plt.axvspan(result['interval_start'], result['interval_end'], color='red', alpha=0.3)
            plt.xlabel('Time')
            plt.ylabel('Active Temp')
            plt.title('Active Temp over Time with Constant Intervals Highlighted')
            plt.legend()
            st.pyplot(plt)

        else:
            st.write("No intervals found where Active Temp is constant for at least 10 seconds within the given tolerance.")

    # Display all Active Temp values along with time column
    #st.write("All Time and Active Temp values:")
    #st.write(df[[time_col, active_Temp_col]].rename(columns={time_col: 'Time', active_Temp_col: 'Active Temp'}))
