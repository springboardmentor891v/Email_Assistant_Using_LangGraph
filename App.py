import streamlit as st
import time
import re
from langgraph.types import Command
from app.core.gmail_client import (
    get_gmail_service, fetch_unread_emails, extract_email, 
    clean_email_body, mark_read
)
from app.agent.graph import build_email_graph
from memoryStore import init_memory, get_sender_history, save_email_memory

# --- 1. SETUP ---
init_memory()
st.set_page_config(page_title="AI Email Assistant", layout="wide")

if "user_email_id" not in st.session_state:
    st.title("📧 AI Email Assistant")
    e_in = st.text_input("Enter Gmail Address:")
    if st.button("Connect"):
        st.session_state.user_email_id = e_in
        st.rerun()
    st.stop()

service, cal_service = get_gmail_service(st.session_state.user_email_id)

# --- 2. FIX: FETCH TOTAL COUNT (4000+) ---
def get_real_counts(service):
    profile = service.users().getProfile(userId='me').execute()
    total_messages = profile.get('messagesTotal', 0)
    unread_results = service.users().messages().list(userId='me', q="is:unread", maxResults=1).execute()
    unread_total = unread_results.get('resultSizeEstimate', 0)
    return unread_total, total_messages - unread_total

def fetch_emails_logic(query=None, show_unread_only=True):
    base_q = "label:INBOX"
    if show_unread_only: base_q += " is:unread"
    final_q = f"{base_q} {query}" if query else base_q
    results = service.users().messages().list(userId='me', q=final_q, maxResults=15).execute()
    messages = results.get('messages', [])
    full_data = []
    for m in messages:
        msg = service.users().messages().get(userId='me', id=m['id']).execute()
        full_data.append(msg)
    return full_data

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    view_opt = st.radio("Display:", ["Unread Only", "All Mail"])
    unread_mode = (view_opt == "Unread Only")
    persona = st.selectbox("Persona", ["Professional Assistant", "Friendly Support"])
    if st.button("Refresh Inbox", use_container_width=True):
        st.session_state.unread_list = fetch_emails_logic(show_unread_only=unread_mode)
        st.rerun()

agent_app = build_email_graph(persona, service, cal_service)
left, center, right = st.columns([1.3, 2.4, 1.3])

# --- 4. LEFT: INBOX ---
with left:
    st.subheader("📨 Inbox")
    s_input = st.text_input("Search", placeholder="Search...", label_visibility="collapsed")
    if st.button("🔍 Search", use_container_width=True):
        st.session_state.unread_list = fetch_emails_logic(query=s_input, show_unread_only=unread_mode)

    st.divider()
    for msg in st.session_state.get("unread_list", []):
        subj = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'Subject'), "No Subject")
        icon = "🔵" if 'UNREAD' in msg.get('labelIds', []) else "⚪"
        if st.button(f"{icon} {subj[:25]}...", key=msg['id'], use_container_width=True):
            st.session_state.selected_msg_id = msg['id']
            st.rerun()

# --- 5. CENTER: PROCESSOR ---
with center:
    st.subheader("📄 Email Processor")
    if m_id := st.session_state.get("selected_msg_id"):
        subj, sender, raw_body, t_id = extract_email(service, m_id)
        
        # FIX: DEFENSIVE UNPACKING
        hist = get_sender_history(sender)
        with st.container(border=True):
            st.markdown(f"**Memory for:** `{sender}`")
            if hist:
                for row in hist:
                    # Accessing by index prevents the "unpacking" error
                    act = row[0] if len(row) > 0 else "Unknown"
                    ts = row[1] if len(row) > 1 else "Unknown Date"
                    st.caption(f"🕒 {ts[:16]} - {act.upper()}")
            else: st.caption("No history in database.")

        st.text_area("Content", clean_email_body(raw_body), height=150)
        res_key = f"res_{m_id}"
        ai_res = st.session_state.get(res_key, {})
        ai_draft = ai_res.get("decision", {}).get("reply", "")
        
        if ai_res and not ai_draft: st.warning("🤖 Agent is ignoring this message.")
        
        reply_box = st.text_area("AI Draft", value=ai_draft, height=150)
        c1, c2 = st.columns(2)
        if c1.button("🤖 Generate", use_container_width=True):
            st.session_state[res_key] = agent_app.invoke({"subject": subj, "sender": sender, "body": raw_body}, config={"configurable": {"thread_id": t_id}})
            st.rerun()
        
        label = "📤 Send" if ai_draft else "👓 Mark as Read"
        if c2.button(label, type="primary", use_container_width=True):
            if ai_draft:
                agent_app.invoke(Command(resume={"final_reply": reply_box}), config={"configurable": {"thread_id": t_id}})
                save_email_memory(sender, subj, t_id, "replied", reply_box)
                st.success("✅ Success: Reply Sent!")
            else:
                save_email_memory(sender, subj, t_id, "ignored", "No reply")
                st.info("✅ Success: Marked as Read")
            
            mark_read(service, m_id)
            if unread_mode: st.session_state.unread_list = [e for e in st.session_state.unread_list if e['id'] != m_id]
            st.session_state.selected_msg_id = None
            time.sleep(1)
            st.rerun()

# --- 6. RIGHT: CHATBOT (Count & Process) ---
with right:
    st.subheader("💬 Assistant")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    chat_box = st.container(height=450)
    for r, t in st.session_state.chat_history: chat_box.chat_message(r).write(t)

    if chat_in := st.chat_input("Ask: 'how many unread?'"):
        st.session_state.chat_history.append(("user", chat_in))
        query = chat_in.lower()

        if any(w in query for w in ["count", "how many", "unread"]):
            u, r = get_real_counts(service)
            ans = f"📊 **Inbox Status:**\n- 🔵 Unread: {u}\n- ⚪ Read: {r}\n- 📦 Total: {u+r}"
        
        elif "process" in query:
            unreads = fetch_unread_emails(service, 20)
            if not unreads: ans = "No unread emails found."
            else:
                num = re.search(r'\d+', query)
                limit = len(unreads) if "all" in query else (int(num.group()) if num else 1)
                limit = min(limit, len(unreads))
                with st.status(f"Processing {limit} emails...") as status:
                    for i in range(limit):
                        m = unreads[i]
                        s, sndr, b, tid = extract_email(service, m['id'])
                        agent_app.invoke({"subject": s, "sender": sndr, "body": b}, config={"configurable": {"thread_id": tid}})
                        save_email_memory(sndr, s, tid, "bulk_processed")
                        mark_read(service, m['id'])
                    status.update(label=f"Finished {limit}!", state="complete")
                ans = f"✅ Processed {limit} emails."
                st.session_state.unread_list = fetch_emails_logic(show_unread_only=unread_mode)
        else: ans = "Try: 'How many unread' or 'Process all'."
        
        st.session_state.chat_history.append(("assistant", ans))
        st.rerun()