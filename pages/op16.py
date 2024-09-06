import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Sample Data Generation Function
def generate_sample_data():
    np.random.seed(0)
    dates = pd.date_range('20230101', periods=100)
    df = pd.DataFrame(np.random.randn(100, 4), index=dates, columns=list('ABCD'))
    df['E'] = df['A'] * 2
    return df

# Function to determine column ranges and assign y-axes
def assign_axes(df, selected_columns):
    column_ranges = {col: df[col].max() - df[col].min() for col in selected_columns}
    sorted_columns = sorted(column_ranges.items(), key=lambda x: x[1], reverse=True)
    sorted_columns = [col for col, _ in sorted_columns]
    return sorted_columns

# Generate sample data
df = generate_sample_data()

# Streamlit App
st.title("Dynamic Y-Axis Plot")

# File uploader (for demonstration, we're using generated data)
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

columns = df.columns.tolist()

# User selects columns to plot
selected_columns = st.multiselect("Select columns to plot", columns, default=columns[:2])

if selected_columns:
    # Assign axes dynamically based on column ranges
    sorted_columns = assign_axes(df, selected_columns)

    # Create Plotly figure
    fig = go.Figure()

    for i, column in enumerate(sorted_columns):
        axis = 'y1' if i == 0 else 'y2'
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[column],
            mode='lines',
            name=f'Mean {column}',
            yaxis=axis
        ))

    # Update layout for multiple y-axes
    fig.update_layout(
        title=f'Mean Values of Selected Parameters',
        xaxis=dict(title='Date'),
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

    # Show plot
    st.plotly_chart(fig, use_container_width=True)
