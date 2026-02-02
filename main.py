# main.py

import os
import sqlite3
from datetime import datetime
from typing import List

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# LangSmith
from langsmith import Client

# Streamlit for UI
import streamlit as st

# ---------------- CONFIG ----------------
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DATABASE_FILE = 'agent_memory.db'
LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY")  # Set in your system environment

# ---------------- LANGSMITH ----------------
langsmith_client = Client(api_key=LANGSMITH_API_KEY)
def log_langsmith(msg: str):
    print("[LangSmith Log]", msg)
    try:
        langsmith_client.create_run(logs=[{"text": msg}])
    except:
        pass  # in case API key not valid

# ---------------- SQLITE ----------------
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            snippet TEXT,
            suggested_reply TEXT,
            received_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id TEXT PRIMARY KEY,
            summary TEXT,
            start_time TEXT,
            end_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_email(email):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO emails (id, sender, subject, snippet, suggested_reply, received_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (email['id'], email['sender'], email['subject'], email['snippet'], email['suggested_reply'], email['received_at']))
    conn.commit()
    conn.close()
    log_langsmith(f"Saved email from {email['sender']}")

def save_calendar_event(event):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO calendar_events (id, summary, start_time, end_time)
        VALUES (?, ?, ?, ?)
    """, (event['id'], event['summary'], event['start'], event['end']))
    conn.commit()
    conn.close()
    log_langsmith(f"Saved calendar event '{event['summary']}'")

# ---------------- GOOGLE API ----------------
def get_service(scopes, creds_file='credentials.json', token_file='token.json'):
    creds = None
    if os.path.exists(token_file) and os.path.getsize(token_file) > 0:
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_gmail_service():
    creds = get_service(GMAIL_SCOPES, token_file='token_gmail.json')
    service = build('gmail', 'v1', credentials=creds)
    log_langsmith("Gmail service authorized")
    return service

def get_calendar_service():
    creds = get_service(CALENDAR_SCOPES, token_file='token_calendar.json')
    service = build('calendar', 'v3', credentials=creds)
    log_langsmith("Calendar service authorized")
    return service

# ---------------- FETCH EMAILS ----------------
def fetch_unread_emails(service, max_results=10) -> List[dict]:
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_detail['payload']['headers']
        sender = next((h['value'] for h in headers if h['name']=='From'), '')
        subject = next((h['value'] for h in headers if h['name']=='Subject'), '')
        snippet = msg_detail.get('snippet', '')
        received_at = msg_detail.get('internalDate', '')

        email = {
            'id': msg['id'],
            'sender': sender,
            'subject': subject,
            'snippet': snippet,
            'received_at': datetime.fromtimestamp(int(received_at)//1000).isoformat() if received_at else '',
            'suggested_reply': ''  # will fill later
        }
        emails.append(email)

    log_langsmith(f"Fetched {len(emails)} unread emails")
    return emails

# ---------------- FETCH CALENDAR EVENTS ----------------
def fetch_calendar_events(service, max_results=10) -> List[dict]:
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=max_results, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    calendar_events = []

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        e = {
            'id': event['id'],
            'summary': event.get('summary', 'No Title'),
            'start': start,
            'end': end
        }
        calendar_events.append(e)

    log_langsmith(f"Fetched {len(calendar_events)} upcoming events")
    return calendar_events

# ---------------- REPLY GENERATION ----------------
def generate_reply(email, events) -> str:
    # If email mentions a time, check for conflicts
    # Simple keyword search for HH:MM or H:MM pattern
    import re
    times = re.findall(r'(\d{1,2}:\d{2})', email['snippet'])
    conflict = False

    for t in times:
        for ev in events:
            if t in ev['start']:
                conflict = True
                break

    if conflict:
        return "Dear, I am busy at that time. Can we reschedule?"
    else:
        return "Dear, I am available. Let's schedule at your suggested time."

# ---------------- STREAMLIT UI ----------------
def launch_ui(emails, events):
    st.title("📧 Email Agent Dashboard")
    st.subheader("Unread Emails & Suggested Replies")
    for e in emails:
        st.markdown(f"**From:** {e['sender']}  \n**Subject:** {e['subject']}  \n**Snippet:** {e['snippet']}  \n**Suggested Reply:** {e['suggested_reply']}")
        st.markdown("---")

    st.subheader("Upcoming Calendar Events")
    for ev in events:
        st.markdown(f"**Event:** {ev['summary']}  \n**Start:** {ev['start']}  \n**End:** {ev['end']}")
        st.markdown("---")

# ---------------- MAIN ----------------
def main():
    init_db()
    gmail_service = get_gmail_service()
    calendar_service = get_calendar_service()

    emails = fetch_unread_emails(gmail_service)
    events = fetch_calendar_events(calendar_service)

    # Generate suggested replies
    for e in emails:
        e['suggested_reply'] = generate_reply(e, events)
        save_email(e)
    for ev in events:
        save_calendar_event(ev)

    print(f"Fetched {len(emails)} emails and {len(events)} calendar events.")
    launch_ui(emails, events)

if __name__ == "__main__":
    main()