import streamlit as st

st.title("📅 AI Calendar Assistant")
st.write("Chat with your calendar agent")

user_input = st.text_input("Enter your request:")

if st.button("Submit"):
    st.write("✅ Button clicked")   # DEBUG LINE
    st.write("You said:", user_input)
