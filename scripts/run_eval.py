import streamlit as st
import time
from app.agent.graph import build_email_graph
from app.core.gmail_client import (
    get_gmail_service, 
    fetch_unread_emails, 
    extract_email, 
    clean_email_body, 
    mark_read
)

# --- PAGE SETUP ---
st.set_page_config(page_title="Email Agent Pro", page_icon="📩", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .email-box { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SERVICES ---
if "services" not in st.session_state:
    with st.spinner("Authenticating..."):
        gmail_svc, cal_svc = get_gmail_service()
        st.session_state.services = (gmail_svc, cal_svc)
        st.session_state.emails = []

gmail_service, calendar_service = st.session_state.services

# --- SIDEBAR: CONFIG ---
with st.sidebar:
    st.title("⚙️ Agent Settings")
    persona = st.selectbox(
        "Select Agent Persona",
        ["Professional Assistant", "Concise Executive", "Friendly Support", "Technical Recruiter"]
    )
    persona_map = {
        "Professional Assistant": "You are a professional assistant. Draft polite and concise replies.",
        "Concise Executive": "You are a busy executive. Keep replies extremely short and to the point.",
        "Friendly Support": "You are a helpful support agent. Use a warm, friendly tone.",
        "Technical Recruiter": "You are a technical recruiter. Be professional and clear about next steps."
    }
    user_prompt = persona_map[persona]
    max_emails = st.slider("Max emails to fetch", 1, 100, 10)
    
    if st.button("🔄 Refresh Inbox", use_container_width=True):
        st.session_state.emails = fetch_unread_emails(gmail_service, max_results=max_emails)
        st.rerun()

agent_app = build_email_graph(user_prompt, gmail_service, calendar_service)

# --- MAIN UI ---
st.title("📩 Email Assistant Dashboard")

query = st.chat_input("Ask me 'How many emails?' or 'see inbox'...")
if query:
    q = query.lower()
    if any(word in q for word in ["how many", "count", "number", "total"]):
        unread_list = fetch_unread_emails(gmail_service, max_results=100)
        unread_count = len(unread_list)
        all_results = gmail_service.users().messages().list(userId='me', maxResults=100).execute()
        total_count = all_results.get('resultSizeEstimate', 0)
        st.chat_message("assistant").write(f"📊 **Total:** {total_count} | **Unread:** {unread_count}")
    elif any(word in q for word in ["see", "inbox"]):
        st.session_state.emails = fetch_unread_emails(gmail_service, max_results=max_emails)
        st.rerun()

# --- DISPLAY EMAILS ---
if not st.session_state.emails:
    st.info("Your inbox is clear.")
else:
    for idx, msg in enumerate(st.session_state.emails):
        subj, sender, body, thread_id = extract_email(gmail_service, msg["id"])
        body = clean_email_body(body)

        with st.container():
            st.markdown(f'<div class="email-box"><b>From:</b> {sender}<br><b>Subject:</b> {subj}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                # 🤖 BUTTON 1: START THE RUN
                if st.button(f"🤖 Process", key=f"proc_{msg['id']}"):
                    state = {"subject": subj, "sender": sender, "body": body, "thread_id": thread_id}
                    config = {"configurable": {"thread_id": thread_id}}
                    # This starts the thread and pauses at the breakpoint
                    result = agent_app.invoke(state, config=config)
                    st.session_state[f"result_{msg['id']}"] = result

            with col2:
                with st.expander("Show Email Content"):
                    st.text(body)

            res_key = f"result_{msg['id']}"
            if res_key in st.session_state:
                res = st.session_state[res_key]
                decision = res.get("decision", {})
                
                st.divider()
                final_draft = st.text_area("Draft Reply", 
                                         value=res.get("final_reply") or decision.get("reply", ""), 
                                         key=f"edit_{msg['id']}", height=150)
                
                c1, c2 = st.columns(2)
                with c1:
                    # ✅ BUTTON 2: RESUME THE SAME RUN
                    if st.button("✅ Confirm & Send", key=f"send_{msg['id']}", type="primary"):
                        config = {"configurable": {"thread_id": thread_id}}
                        
                        # STEP 1: Update the EXISTING thread memory with the user's edit
                        agent_app.update_state(config, {"final_reply": final_draft})
                        
                        # STEP 2: Tell the app to continue from where it left off (the breakpoint)
                        # By passing 'None', it resumes the EXISTING run row in LangSmith
                        # instead of creating a new row.
                        agent_app.invoke(None, config=config)
                        
                        mark_read(gmail_service, msg["id"])
                        st.success("Sent!")
                        del st.session_state[res_key]
                        st.rerun()
                with c2:
                    if st.button("🗑️ Discard", key=f"disc_{msg['id']}"):
                        del st.session_state[res_key]
                        st.rerun()