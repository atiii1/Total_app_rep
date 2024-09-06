import streamlit as st # type: ignore
#import pandas as pd
#import numpy as np 

data1 = "this is the test action of button."
st.title("first app")
# Change font and color of title
st.markdown("<h1 style='color: blue; font-family: Arial;'>Custom Title</h1>", unsafe_allow_html=True)

st.write("Hello beautiful world!")

x = st.text_input("enter fav var")
st.write(f"your favarite var is: {x}")

is_clicked1 = st.button("Button 1", key="button1")

if is_clicked1:
    st.write("Button 1 clicked!")

is_clicked2 = st.button("Button 2", key="button2")

if is_clicked2:
    st.write("Button 2 clicked!")




# Change font and color of text
st.markdown("<h1 style='color: blue;'>This is a header with blue color</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-family: Arial;'>This is a paragraph with Arial font</p>", unsafe_allow_html=True)
st.markdown("<p style='color: green; font-size: 20px;'>This is a paragraph with green color and font size 20px</p>", unsafe_allow_html=True)


# Change size and color of buttons
st.markdown("""
    <style>
        .stButton>button {
            background-color: #ff5733; /* Change button background color */
            color: white; /* Change button text color */
            padding: 10px 20px; /* Change button padding */
            font-size: 16px; /* Change button font size */
            border-radius: 5px; /* Change button border radius */
        }
    </style>
""", unsafe_allow_html=True)

button_clicked = st.button("Click me!")
if button_clicked:
    st.write("Button vvvvv clicked!")



# Define CSS styles for different button styles
button_style_1 = """
    <style>
        .button-1 {
            background-color: #ff5733; /* Change button background color */
            color: white; /* Change button text color */
            padding: 10px 20px; /* Change button padding */
            font-size: 16px; /* Change button font size */
            border-radius: 5px; /* Change button border radius */
        }
    </style>
"""
button_style_2 = """
    <style>
        .button-2 {
            background-color: #3498db; /* Change button background color */
            color: white; /* Change button text color */
            padding: 15px 25px; /* Change button padding */
            font-size: 18px; /* Change button font size */
            border-radius: 10px; /* Change button border radius */
        }
    </style>
"""

# Apply CSS styles using st.markdown()
st.markdown(button_style_1, unsafe_allow_html=True)
st.markdown(button_style_2, unsafe_allow_html=True)

# Create buttons with different styles using HTML
button_clicked1 = st.markdown("<button class='button-1'>Button 1</button>", unsafe_allow_html=True)
button_clicked2 = st.markdown("<button class='button-2'>Button 2</button>", unsafe_allow_html=True)
