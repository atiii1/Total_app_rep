import streamlit as st # type: ignore
import pandas as pd

file_name = 'E72606V902 - art data.xlsx'
data_t = pd.read_excel(file_name , sheet_name= '1280100-1')

st.write(data_t)