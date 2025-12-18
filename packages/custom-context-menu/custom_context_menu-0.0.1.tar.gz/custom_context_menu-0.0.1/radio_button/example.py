import streamlit as st
from radio_button import custom_context_menu

result = custom_context_menu()
st.write("You selected:", result)
