import streamlit as st
from st_button import custom_button

st.title("My Custom Component")

result = custom_button("Press the button")
st.write("Result:", result)
