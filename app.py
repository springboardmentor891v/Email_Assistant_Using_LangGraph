import streamlit as st
from auth import get_gmail_service
from gmail_utils import fetch_emails, send_email
from ai import generate_reply

st.set_page_config(page_title="Agentic AI", layout="wide")

if "gmail_service" not in st.session_state:
    st.session_state.gmail_service = None

if "selected_email" not in st.session_state:
    st.session_state.selected_email = None

st.sidebar.title("📧 Agentic AI")
menu = st.sidebar.radio(
    "Navigation",
    ["Connect to Gmail", "Inbox", "Email studio", "Calendar", "Insights", "Settings"]
)

# CONNECT
if menu == "Connect to Gmail":
    st.title("Connect to Gmail")

    if st.button("🔗 Connect to Gmail"):
        st.session_state.gmail_service = get_gmail_service()
        st.success("Gmail connected successfully!")

# INBOX
elif menu == "Inbox":
    st.title("📥 Inbox")

    if not st.session_state.gmail_service:
        st.warning("Please connect to Gmail first.")
    else:
        emails = fetch_emails(st.session_state.gmail_service, max_results=10)

        for i, email in enumerate(emails):
            if st.button(f"{email['subject']} - {email['from']}", key=i):
                st.session_state.selected_email = email

        if st.session_state.selected_email:
            email = st.session_state.selected_email
            st.divider()
            st.subheader(email["subject"])
            st.write(email["body"])

            st.subheader("🤖 AI Reply Assistant")
            reply = generate_reply(email["body"])
            reply_text = st.text_area("Generated Reply", reply, height=150)

            if st.button("✅ Confirm & Send Reply"):
                send_email(
                    st.session_state.gmail_service,
                    email["from"],
                    "Re: " + email["subject"],
                    reply_text
                )
                st.success("Reply sent successfully!")

# EMAIL STUDIO
elif menu == "Email studio":
    st.title("✍️ Email Studio")

    to = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    body = st.text_area("Draft Reply")

    if st.button("Enhance with AI"):
        st.text_area("AI Enhanced Reply", generate_reply(body))

# CALENDAR
elif menu == "Calendar":
    st.title("📅 Calendar")
    st.info("Meeting detection and calendar automation planned.")

# INSIGHTS
elif menu == "Insights":
    st.title("📊 Insights")
    st.bar_chart({"Emails": [5, 8, 6, 10, 7]})

# SETTINGS
elif menu == "Settings":
    st.title("⚙️ Settings")
    st.write("Reply tone: Professional")
    st.write("Reply length: Short")