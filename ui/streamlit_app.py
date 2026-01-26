import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from app_tools.open_ai import generate_reply

st.title("📧 Email Assistant")

email_body = st.text_area("Paste email content")

if st.button("Generate Reply"):
    reply = generate_reply(
        subject="Demo",
        sender="user@example.com",
        body=email_body
    )
    st.text_area("Generated Reply", reply, height=200)
