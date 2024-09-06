import streamlit as st
from PIL import Image

# Load the image
logo = Image.open("hf_logo.png")

# Display the image at the top of the app
st.image(logo, width=200)  # Adjust the width as needed

st.title("Data Analysis Application")

st.write("Use the sidebar to navigate through the pages.")