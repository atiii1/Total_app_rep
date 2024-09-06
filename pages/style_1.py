import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

import plotly.express as px

st.markdown(
    """
    <style>
    .title {
        font-size: 50px;
        color: #4CAF50;
        text-align: center;
        font-family: 'Arial';
    }
    .header {
        font-size: 30px;
        color: #2196F3;
        text-align: left;
        font-family: 'Helvetica';
    }
    .subheader {
        font-size: 24px;
        color: #FF5722;
        text-align: left;
        font-family: 'Courier New';
    }
    </style>
    """, unsafe_allow_html=True
)

# Usage in your app
st.markdown('<div class="title">My Streamlit App</div>', unsafe_allow_html=True)
st.markdown('<div class="header">Section 1</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Subsection 1.1</div>', unsafe_allow_html=True)





# Example data
df = px.data.iris()

# Plotly figure
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", title="Scatter plot of Sepal Width vs Length")

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.title("My Streamlit App")

# Columns
col1, col2 = st.columns(2)

with col1:
    st.header("Column 1")
    st.write("Content for column 1")

with col2:
    st.header("Column 2")
    st.write("Content for column 2")



# Expander
with st.expander("More Info"):
    st.write("Here you can put additional information that is initially hidden.")

    st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home", "About", "Contact"])

if page == "Home":
    st.title("Welcome to the Home Page")
elif page == "About":
    st.title("About Us")
else:
    st.title("Contact Us")


st.markdown("""
# My App
**Bold Text**

*Italic Text*

- Bullet Point 1
- Bullet Point 2

> Blockquote
""")



df = pd.DataFrame({
    'Column A': [1, 2, 3],
    'Column B': [4, 5, 6]
})

st.dataframe(df.style.highlight_max(axis=0))


st.video("https://www.youtube.com/watch?v=JfVOs4VSpmA")
st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

st.markdown("# 🚀 My Streamlit App")
st.markdown("## 📈 Analytics Section")
st.markdown("### 🔧 Settings")

