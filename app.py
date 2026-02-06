import streamlit as st
from calendar_service import get_events   # keep this if you already added it

st.set_page_config(page_title="Calendar Assistant")

st.title("📅 AI Calendar Assistant")
st.write("Chat with your calendar agent")

user_input = st.text_input("Enter your request:")

if st.button("Submit"):
    if user_input:
        st.success(f"You said: {user_input}")
    else:
        st.warning("Please enter something")

