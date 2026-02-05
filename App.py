import streamlit as st
import time
from langgraph.types import Command
from app.core.gmail_client import (
    get_gmail_service, fetch_unread_emails, extract_email, 
    clean_email_body, mark_read, get_email_counts
)
from app.agent.graph import build_email_graph

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Email Assistant", layout="wide")

# --- 1. LOGIN / IDENTITY ---
if "user_email_id" not in st.session_state:
    st.title("📧 AI Email Assistant")
    email_in = st.text_input("Enter your Gmail address to start:")
    if st.button("Connect Account"):
        if email_in:
            st.session_state.user_email_id = email_in
            st.rerun()
    st.stop()

# --- 2. INIT SERVICES ---
@st.cache_resource
def init_services(email):
    # Returns (gmail_service, calendar_service)
    return get_gmail_service(email)

service, calendar_service = init_services(st.session_state.user_email_id)

# --- 3. SESSION STATE ---
if "unread_list" not in st.session_state: st.session_state.unread_list = []
if "selected_msg_id" not in st.session_state: st.session_state.selected_msg_id = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.write(f"User: **{st.session_state.user_email_id}**")
    persona = st.selectbox("Agent Persona", ["Professional Assistant", "Friendly Support"])
    
    if st.button("📥 Refresh Unread", use_container_width=True):
        # Specifically fetch unread to avoid full inbox clutter
        st.session_state.unread_list = fetch_unread_emails(service, 10)
        st.rerun()

# Build agent
agent_app = build_email_graph(persona, service, calendar_service)

# --- 5. THREE COLUMN LAYOUT ---
left, center, right = st.columns([1.2, 2.5, 1.3])

# LEFT: INBOX LIST (Sender & Subject)
with left:
    st.subheader("📨 Unread")
    if not st.session_state.unread_list:
        st.info("No unread emails.")
    else:
        for msg in st.session_state.unread_list:
            headers = msg['payload']['headers']
            subj = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sndr = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown").split('<')[0].strip()
            
            # Use Sender + Subject for clear sidebar labels
            if st.button(f"👤 {sndr}\n📧 {subj[:25]}...", key=msg['id'], use_container_width=True):
                st.session_state.selected_msg_id = msg['id']

# CENTER: EMAIL VIEWER & SINGLE-ROW TRACE LOGIC
with center:
    st.subheader("📄 Viewer")
    if m_id := st.session_state.selected_msg_id:
        # Extract and clean HTML/CSS body
        subj, sender, raw_body, t_id = extract_email(service, m_id)
        clean_text = clean_email_body(raw_body)
        
        st.markdown(f"**From:** `{sender}`")
        st.markdown(f"**Subject:** `{subj}`")
        st.text_area("Email Content", clean_text, height=200)
        
        # THREAD CONFIG (Crucial for LangSmith single-row grouping)
        config = {"configurable": {"thread_id": t_id}}
        res_key = f"res_{m_id}"
        
        ai_draft = st.session_state.get(res_key, {}).get("decision", {}).get("reply", "")
        reply_box = st.text_area("✍️ AI Draft Reply", value=ai_draft, height=150, key=f"box_{m_id}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🤖 AI Process", use_container_width=True):
                try:
                    # Starts the trace row
                    state = {"subject": subj, "sender": sender, "body": clean_text, "thread_id": t_id}
                    st.session_state[res_key] = agent_app.invoke(state, config=config)
                    st.rerun()
                except Exception as e:
                    # Catch 404 or 429 quota errors gracefully
                    st.error(f"AI Error: {str(e)}")
        with c2:
            if st.button("📤 Confirm & Send", type="primary", use_container_width=True):
                try:
                    # RESUME: This prevents the 'null' input and multiple rows issue
                    agent_app.invoke(Command(resume={"final_reply": reply_box}), config=config)
                    mark_read(service, m_id)
                    st.success("Thread completed in a single row!")
                    
                    # Cleanup local state
                    st.session_state.unread_list = [e for e in st.session_state.unread_list if e['id'] != m_id]
                    st.session_state.selected_msg_id = None
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Send Error: {str(e)}")
    else:
        st.info("Select an unread email to view.")

# RIGHT: INTERACTIVE CHATBOT
with right:
    st.subheader("💬 Assistant")
    chat_container = st.container(height=400)
    
    for role, text in st.session_state.chat_history:
        chat_container.chat_message(role).write(text)
    
    if prompt := st.chat_input("Ask: 'tell me my inbox'"):
        st.session_state.chat_history.append(("user", prompt))
        cmd = prompt.lower()
        
        # Chatbot logic for metadata counts
        if any(w in cmd for w in ["tell me", "unread", "draft", "inbox"]):
            u, r, d = get_email_counts(service)
            response = (f"📊 **Inbox Status:**\n\n* Unread: {u}\n* Read: {r}\n* Drafts: {d}")
            st.session_state.chat_history.append(("assistant", response))
        else:
            st.session_state.chat_history.append(("assistant", "I can check your mail counts or help process drafts."))
        st.rerun()