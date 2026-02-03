import streamlit as st
from dotenv import load_dotenv
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from auth.gmail_auth import get_gmail_service
from auth.calendar_auth import get_calendar_service
from app_tools.gmail_reader import get_unread_emails, read_email
from app_tools.gmail_sender import send_reply, mark_as_read
from app_tools.open_ai import generate_reply_unified, extract_and_check_event
from app_tools.calender_tools import create_event, has_conflict, suggest_free_slots
from memory.memory_store import init_db, get_feedback, save_feedback
from evaluation.evaluators import judge_reply
from datetime import datetime, timezone
import json

# Page configuration
st.set_page_config(
    page_title="Email Assistant Pro",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "gmail_service" not in st.session_state:
    st.session_state.gmail_service = None
if "calendar_service" not in st.session_state:
    st.session_state.calendar_service = None
if "emails" not in st.session_state:
    st.session_state.emails = []
if "selected_email" not in st.session_state:
    st.session_state.selected_email = None

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .email-item {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff6b6b;
        margin: 10px 0;
        cursor: pointer;
    }
    .email-item.important {
        border-left-color: #ff6b6b;
    }
    .email-item.promotional {
        border-left-color: #ffd43b;
    }
    .email-item.social {
        border-left-color: #4c6ef5;
    }
    .email-item.other {
        border-left-color: #51cf66;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def normalize(dt_str: str) -> str:
    """Convert ISO datetime to RFC3339 UTC."""
    if dt_str.endswith("Z"):
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def categorize_email(subject: str, body: str) -> str:
    """Categorize email based on content."""
    content = (subject + " " + body).lower()
    
    if any(word in content for word in ["promotion", "sale", "discount", "offer", "limited time", "deal"]):
        return "promotional"
    elif any(word in content for word in ["facebook", "twitter", "linkedin", "instagram", "social"]):
        return "social"
    elif any(word in content for word in ["urgent", "important", "asap", "critical", "meeting", "zoom", "call", "conference", "discuss", "schedule", "calendar", "appointment", "sync", "standup", "retro", "planning"]):
        return "important"
    else:
        return "other"


def load_emails():
    """Load unread emails from Gmail."""
    try:
        if st.session_state.gmail_service is None:
            st.session_state.gmail_service = get_gmail_service()
        
        emails = get_unread_emails(st.session_state.gmail_service, max_results=15)
        
        email_details = []
        for email in emails:
            msg_id = email["id"]
            thread_id = email["threadId"]
            subject, sender, body = read_email(st.session_state.gmail_service, msg_id)
            
            category = categorize_email(subject, body)
            
            email_details.append({
                "id": msg_id,
                "thread_id": thread_id,
                "subject": subject,
                "sender": sender,
                "body": body,
                "category": category,
                "timestamp": datetime.now()
            })
        
        st.session_state.emails = email_details
        return email_details
    except Exception as e:
        st.error(f"Error loading emails: {str(e)}")
        return []


def get_email_stats():
    """Calculate email statistics."""
    total = len(st.session_state.emails)
    important = sum(1 for e in st.session_state.emails if e["category"] == "important")
    promotional = sum(1 for e in st.session_state.emails if e["category"] == "promotional")
    social = sum(1 for e in st.session_state.emails if e["category"] == "social")
    other = sum(1 for e in st.session_state.emails if e["category"] == "other")
    
    return {
        "total": total,
        "important": important,
        "promotional": promotional,
        "social": social,
        "other": other
    }


def save_evaluation(score):
    """Save evaluation score to memory store."""
    # Get existing evaluations
    existing = get_feedback("evaluations")
    evaluations_list = []
    
    if existing:
        try:
            if isinstance(existing, str):
                evaluations_list = json.loads(existing)
            elif isinstance(existing, list):
                evaluations_list = existing
        except:
            evaluations_list = []
    
    # Add new evaluation
    evaluations_list.append(score)
    
    # Keep only last 50 evaluations
    if len(evaluations_list) > 50:
        evaluations_list = evaluations_list[-50:]
    
    # Save back
    save_feedback("evaluations", json.dumps(evaluations_list))


def get_calendar_events():
    """Fetch upcoming calendar events."""
    if not st.session_state.calendar_service:
        return []
    
    try:
        from datetime import datetime, timedelta
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Get events for next 30 days
        events_result = st.session_state.calendar_service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
    except Exception as e:
        st.error(f"Error fetching calendar events: {str(e)}")
        return []


# Main UI
st.title("📧 Email Assistant Pro")
st.markdown("Your intelligent email management and reply generation system")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    if st.button("🔄 Connect to Gmail", key="connect_btn"):
        try:
            st.session_state.gmail_service = get_gmail_service()
            st.session_state.calendar_service = get_calendar_service()
            init_db()
            st.success("✅ Connected to Gmail & Calendar!")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
    
    st.divider()
    
    if st.button("📥 Refresh Emails", key="refresh_btn"):
        with st.spinner("Loading emails..."):
            load_emails()
            st.success("✅ Emails loaded!")
    
    st.divider()
    
    # Preferences
    st.subheader("⚙️ Preferences")
    
    # Load saved preferences
    saved_tone = get_feedback("tone") or "professional"
    saved_verbosity = get_feedback("verbosity") or "medium"
    
    tone = st.selectbox(
        "Reply Tone",
        ["professional", "friendly", "formal", "casual"],
        index=["professional", "friendly", "formal", "casual"].index(saved_tone),
        key="tone_select"
    )
    
    verbosity = st.selectbox(
        "Reply Length",
        ["short", "medium", "long"],
        index=["short", "medium", "long"].index(saved_verbosity),
        key="verbosity_select"
    )
    
    # Save preferences when they change
    if tone != saved_tone or verbosity != saved_verbosity:
        save_feedback("tone", tone)
        save_feedback("verbosity", verbosity)
        st.success(f"✅ Preferences saved! (Tone: {tone}, Length: {verbosity})")
    
    st.divider()
    
    st.markdown("""
    ### 📊 Quick Stats
    Total Unread: **{total}**
    
    🔴 Important: **{important}**
    🟡 Promotional: **{promotional}**
    🔵 Social: **{social}**
    🟢 Other: **{other}**
    """.format(**get_email_stats()))


# Main content area
if not st.session_state.emails:
    st.info("👈 Click 'Connect to Gmail' and 'Refresh Emails' to get started!")
else:
    # Dashboard metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    stats = get_email_stats()
    
    with col1:
        st.metric("📬 Total", stats["total"])
    with col2:
        st.metric("🔴 Important", stats["important"])
    with col3:
        st.metric("🟡 Promotional", stats["promotional"])
    with col4:
        st.metric("🔵 Social", stats["social"])
    with col5:
        st.metric("🟢 Other", stats["other"])
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📬 Inbox", "✍️ Reply Manager", "� Analytics", "📅 Calendar"])
    
    with tab1:
        st.subheader("Your Emails")
        
        # Filter emails
        filter_category = st.selectbox(
            "Filter by category",
            ["All", "important", "promotional", "social", "other"],
            key="filter_select"
        )
        
        filtered_emails = st.session_state.emails
        if filter_category != "All":
            filtered_emails = [e for e in st.session_state.emails if e["category"] == filter_category]
        
        if not filtered_emails:
            st.info("No emails in this category")
        else:
            for idx, email in enumerate(filtered_emails):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    category_emoji = {
                        "important": "🔴",
                        "promotional": "🟡",
                        "social": "🔵",
                        "other": "🟢"
                    }
                    
                    if st.button(
                        f"{category_emoji.get(email['category'], '📧')} {email['subject'][:60]}\n"
                        f"From: {email['sender'][:50]}",
                        key=f"email_btn_{idx}",
                        use_container_width=True
                    ):
                        st.session_state.selected_email = idx
                
                with col2:
                    if st.button("✓", key=f"mark_read_{idx}", help="Mark as read"):
                        mark_as_read(st.session_state.gmail_service, email["id"])
                        st.success("Marked as read!")
                        st.rerun()
        
        # Email detail view
        if st.session_state.selected_email is not None:
            st.divider()
            email = filtered_emails[st.session_state.selected_email]
            
            st.subheader(f"📧 {email['subject']}")
            st.caption(f"From: {email['sender']}")
            
            with st.expander("Full Email Content", expanded=True):
                st.text_area("Email Body", email["body"], height=200, disabled=True)
            
            # Auto-reply generation
            st.subheader("🤖 AI Reply Assistant")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                auto_reply = st.checkbox("Generate reply automatically", value=True)
            
            if auto_reply or st.button("Generate Reply", key="gen_reply_btn"):
                with st.spinner("Generating reply..."):
                    # Extract event info
                    should_event, details = extract_and_check_event(email["body"])
                    
                    reply = generate_reply_unified(
                        subject=email["subject"],
                        sender=email["sender"],
                        body=email["body"]
                    )
                
                st.text_area("Generated Reply", reply, height=200, key="reply_area")
                
                # Evaluate reply
                with st.spinner("Evaluating reply quality..."):
                    score = judge_reply(email["body"], reply)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✨ Relevance", f"{score.get('relevance', 0)}/10")
                with col2:
                    st.metric("😊 Politeness", f"{score.get('politeness', 0)}/10")
                with col3:
                    st.metric("✅ Correctness", f"{score.get('correctness', 0)}/10")
                
                # Event detection
                if should_event and details:
                    st.info(f"📅 Event Detected: {details.get('title', 'Unknown')}")
                    
                    add_to_calendar = st.checkbox("Add to calendar", value=True)
                    
                    if add_to_calendar:
                        # Check for conflicts FIRST before showing button
                        start = normalize(details["start_datetime"])
                        end = normalize(details["end_datetime"])
                        has_cal_conflict = has_conflict(st.session_state.calendar_service, start, end)
                        
                        if has_cal_conflict:
                            st.warning("⚠️ Calendar conflict detected!")
                            free_slots = suggest_free_slots(st.session_state.calendar_service, details["start_datetime"].split("T")[0])
                            st.info(f"📅 Free alternative slots: {', '.join(free_slots)}")
                            
                            # Regenerate reply with conflict awareness and available slots
                            with st.spinner("Regenerating reply with available slots..."):
                                updated_reply = generate_reply_unified(
                                    subject=email["subject"],
                                    sender=email["sender"],
                                    body=email["body"],
                                    alternative_slots=free_slots
                                )
                            
                            # Display the conflict-aware reply
                            st.text_area("Generated Reply (With Alternative Times)", updated_reply, height=250, key="reply_area_conflict")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("Send Reply (Skip Event)", key="send_no_event_btn", help="Send reply without creating event"):
                                    try:
                                        send_reply(
                                            st.session_state.gmail_service,
                                            email["sender"],
                                            email["subject"],
                                            updated_reply,
                                            email["thread_id"]
                                        )
                                        mark_as_read(st.session_state.gmail_service, email["id"])
                                        save_evaluation(score)  # Save the evaluation score
                                        st.success("✅ Reply sent! (Event not created due to conflict)")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            with col2:
                                if st.button("Force Create & Send", key="force_create_btn", help="Create event anyway and send reply"):
                                    try:
                                        create_event(
                                            st.session_state.calendar_service,
                                            details["title"],
                                            details.get("description", ""),
                                            details["start_datetime"],
                                            details["end_datetime"]
                                        )
                                        st.warning("📅 Event created (overlapping with existing event)")
                                        
                                        send_reply(
                                            st.session_state.gmail_service,
                                            email["sender"],
                                            email["subject"],
                                            updated_reply,
                                            email["thread_id"]
                                        )
                                        mark_as_read(st.session_state.gmail_service, email["id"])
                                        save_evaluation(score)  # Save the evaluation score
                                        st.success("✅ Reply sent!")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        else:
                            if st.button("Confirm & Send Reply", key="send_btn"):
                                try:
                                    create_event(
                                        st.session_state.calendar_service,
                                        details["title"],
                                        details.get("description", ""),
                                        details["start_datetime"],
                                        details["end_datetime"]
                                    )
                                    st.success("📅 Event created!")
                                    
                                    send_reply(
                                        st.session_state.gmail_service,
                                        email["sender"],
                                        email["subject"],
                                        reply,
                                        email["thread_id"]
                                    )
                                    mark_as_read(st.session_state.gmail_service, email["id"])
                                    save_evaluation(score)  # Save the evaluation score
                                    st.success("✅ Reply sent!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    else:
                        if st.button("Send Reply (No Calendar Event)", key="send_with_checkbox_btn"):
                            try:
                                send_reply(
                                    st.session_state.gmail_service,
                                    email["sender"],
                                    email["subject"],
                                    reply,
                                    email["thread_id"]
                                )
                                mark_as_read(st.session_state.gmail_service, email["id"])
                                save_evaluation(score)  # Save the evaluation score
                                st.success("✅ Reply sent!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                else:
                    if st.button("Send Reply", key="send_simple_btn"):
                        try:
                            send_reply(
                                st.session_state.gmail_service,
                                email["sender"],
                                email["subject"],
                                reply,
                                email["thread_id"]
                            )
                            mark_as_read(st.session_state.gmail_service, email["id"])
                            save_evaluation(score)  # Save the evaluation score
                            st.success("✅ Reply sent!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            # Skip button outside of reply generation
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col3:
                if st.button("⏭️ Skip Email", key="skip_email_btn", help="Skip this email and move to next"):
                    # Clear selection to deselect current email
                    st.session_state.selected_email = None
                    st.info("Email skipped! Select another email from the list.")
                    time.sleep(0.5)
                    st.rerun()
    
    with tab2:
        st.subheader("📝 Manual Reply Composer")
        
        sender = st.text_input("Recipient Email:", placeholder="recipient@example.com")
        subject = st.text_input("Subject:", placeholder="Re: Your email")
        
        manual_reply = st.text_area(
            "Compose your reply:",
            placeholder="Type your message here...",
            height=250
        )
        
        if st.button("💬 Polish Reply with AI", key="polish_btn"):
            with st.spinner("Improving your reply..."):
                # Simple enhancement
                improved = generate_reply_unified(
                    subject=subject,
                    sender=sender,
                    body=manual_reply
                )
                st.text_area("AI-Enhanced Reply", improved, height=200, key="enhanced_reply")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Send Reply", key="send_manual_btn"):
                if sender and subject and manual_reply:
                    try:
                        if not st.session_state.gmail_service:
                            st.error("❌ Gmail not connected. Please click 'Connect to Gmail' in the sidebar.")
                        else:
                            # Send the email
                            send_reply(
                                st.session_state.gmail_service,
                                sender,
                                subject,
                                manual_reply,
                                thread_id=None  # No thread ID for manual composer
                            )
                            st.success("✅ Email sent successfully!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error sending email: {str(e)}")
                else:
                    st.error("Please fill in all fields: Recipient, Subject, and Message")
        
        with col2:
            if st.button("🗑️ Clear", key="clear_btn"):
                st.rerun()
    
    with tab3:
        st.subheader("📊 Email Analytics")
        
        stats = get_email_stats()
        
        # Category distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Unread Emails", stats["total"])
            
            categories = {
                "🔴 Important": stats["important"],
                "🟡 Promotional": stats["promotional"],
                "🔵 Social": stats["social"],
                "🟢 Other": stats["other"]
            }
            
            for category, count in categories.items():
                percentage = (count / stats["total"] * 100) if stats["total"] > 0 else 0
                st.write(f"{category}: {count} ({percentage:.1f}%)")
        
        with col2:
            if stats["total"] > 0:
                chart_data = {
                    "Important": stats["important"],
                    "Promotional": stats["promotional"],
                    "Social": stats["social"],
                    "Other": stats["other"]
                }
                st.bar_chart(chart_data)
        
        st.divider()
        
        # Email response stats
        st.subheader("Response Statistics")
        
        # Calculate actual evaluation stats from memory store
        from memory.memory_store import get_feedback
        all_evaluations = get_feedback("evaluations") or []
        
        if all_evaluations:
            # Parse evaluations
            evaluations_list = []
            if isinstance(all_evaluations, str):
                try:
                    evaluations_list = json.loads(all_evaluations)
                except:
                    evaluations_list = []
            elif isinstance(all_evaluations, list):
                evaluations_list = all_evaluations
            
            if evaluations_list:
                avg_relevance = sum(e.get("relevance", 0) for e in evaluations_list) / len(evaluations_list)
                avg_politeness = sum(e.get("politeness", 0) for e in evaluations_list) / len(evaluations_list)
                avg_correctness = sum(e.get("correctness", 0) for e in evaluations_list) / len(evaluations_list)
                
                st.info(f"Average reply quality: {(avg_relevance + avg_politeness + avg_correctness) / 3:.1f}/10 (based on {len(evaluations_list)} replies)")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Relevance", f"{avg_relevance:.1f}/10")
                with col2:
                    st.metric("Avg Politeness", f"{avg_politeness:.1f}/10")
                with col3:
                    st.metric("Avg Correctness", f"{avg_correctness:.1f}/10")
            else:
                st.info("No evaluations yet. Send and evaluate replies to see statistics.")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Relevance", "-/10")
                with col2:
                    st.metric("Avg Politeness", "-/10")
                with col3:
                    st.metric("Avg Correctness", "-/10")
        else:
            st.info("No evaluations yet. Send and evaluate replies to see statistics.")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Relevance", "-/10")
            with col2:
                st.metric("Avg Politeness", "-/10")
            with col3:
                st.metric("Avg Correctness", "-/10")
    
    with tab4:
        st.subheader("📅 Calendar Events")
        
        if not st.session_state.calendar_service:
            st.warning("📌 Please connect to Gmail first to view calendar events")
        else:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Calendar", key="refresh_cal_btn"):
                    st.rerun()
            
            # Fetch calendar events
            events = get_calendar_events()
            
            if not events:
                st.info("No upcoming events scheduled. Create a calendar event from an email!")
            else:
                # Display events as a table
                st.subheader(f"Upcoming Events ({len(events)})")
                
                # Format events for display
                event_data = []
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    # Parse datetime if available
                    try:
                        if 'T' in start:
                            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                            start_str = start_dt.strftime("%b %d, %I:%M %p")
                        else:
                            start_str = start
                    except:
                        start_str = start
                    
                    event_data.append({
                        "📅 Event": event.get('summary', 'Untitled'),
                        "⏰ Start": start_str
                    })
                
                st.dataframe(
                    event_data,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show event details
                st.subheader("Event Details")
                selected_event_idx = st.selectbox(
                    "Select an event to view details:",
                    range(len(events)),
                    format_func=lambda i: events[i].get('summary', f'Event {i+1}'),
                    key="event_select"
                )
                
                if selected_event_idx is not None:
                    event = events[selected_event_idx]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Title:** {event.get('summary', 'N/A')}")
                        st.write(f"**Description:** {event.get('description', 'N/A')}")
                        st.write(f"**Location:** {event.get('location', 'N/A')}")
                    
                    with col2:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        end = event['end'].get('dateTime', event['end'].get('date'))
                        st.write(f"**Start:** {start}")
                        st.write(f"**End:** {end}")
                        
                        attendees = event.get('attendees', [])
                        if attendees:
                            st.write(f"**Attendees ({len(attendees)}):**")
                            for attendee in attendees:
                                email = attendee.get('email', 'Unknown')
                                response = attendee.get('responseStatus', 'unknown')
                                st.write(f"  • {email} ({response})")


# Footer
st.divider()
st.markdown("""
---
**Email Assistant Pro** | Powered by LangGraph & Groq LLM | LangSmith Enabled
""")
