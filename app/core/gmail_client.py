import os
import base64
import re
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/calendar"]

def get_gmail_service(user_email: str):
    token_file = f"token_{user_email}.json"
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials1.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds), build("calendar", "v3", credentials=creds)

def fetch_unread_emails(service, max_results=10):
    """Fetches ONLY unread emails and includes metadata for the sidebar."""
    # We query specifically for 'is:unread'
    results = service.users().messages().list(userId="me", q="is:unread", maxResults=max_results).execute()
    messages = results.get("messages", [])
    
    detailed_messages = []
    for msg in messages:
        # Fetching full format to get headers (Sender/Subject) for the inbox list
        m = service.users().messages().get(userId="me", id=msg['id'], format='full').execute()
        detailed_messages.append(m)
    return detailed_messages

def extract_email(service, msg_id):
    """Extracts cleaned content for the viewer."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    headers = msg["payload"]["headers"]
    
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
    
    body = ""
    payload = msg["payload"]
    
    # Logic to find the best part of the email body
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] in ["text/plain", "text/html"]:
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                    if part["mimeType"] == "text/plain": break 
    else:
        data = payload["body"].get("data")
        if data: body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        
    return subject, sender, body, msg["threadId"]

def clean_email_body(body: str) -> str:
    """Removes HTML tags and CSS like you saw in image_de1921.png."""
    if not body: return ""
    
    # If it contains HTML, parse it out
    if "<html>" in body.lower() or "<div" in body.lower() or "<!doctype" in body.lower():
        soup = BeautifulSoup(body, "html.parser")
        # Kill CSS and Script tags
        for extra in soup(["script", "style", "head", "title", "meta"]):
            extra.decompose()
        body = soup.get_text(separator=' ')

    # Remove old thread replies and JSON blocks
    body = re.sub(r"```json[\s\S]*?```", "", body, flags=re.IGNORECASE)
    body = re.split(r"\nOn .* wrote:", body)[0]
    return body.strip()

def send_reply(service, to, subject, reply, thread_id):
    message = MIMEText(reply)
    message["to"] = to
    message["subject"] = "Re: " + subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw, "threadId": thread_id}).execute()

def mark_read(service, msg_id):
    service.users().messages().modify(userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()

def get_email_counts(service):
    """Fetches counts for Unread, Read, and Draft emails."""
    # Fetch Unread
    unread = service.users().messages().list(userId='me', q="is:unread").execute()
    unread_count = unread.get('resultSizeEstimate', 0)

    # Fetch Read (not unread)
    read = service.users().messages().list(userId='me', q="is:read").execute()
    read_count = read.get('resultSizeEstimate', 0)

    # Fetch Drafts
    drafts = service.users().drafts().list(userId='me').execute()
    draft_count = len(drafts.get('drafts', []))

    return unread_count, read_count, draft_count

def process_all_unread(service, agent_app, persona):
    """Automatically drafts replies for all unread emails."""
    unread_msgs = fetch_unread_emails(service, max_results=20)
    processed_count = 0
    
    for msg in unread_msgs:
        subj, sender, body, t_id = extract_email(service, msg['id'])
        clean_text = clean_email_body(body)
        
        # Invoke agent to generate draft
        state = {"subject": subj, "sender": sender, "body": clean_text, "thread_id": t_id}
        # Note: We don't send automatically here for safety, just draft in LangSmith/State
        agent_app.invoke(state, config={"configurable": {"thread_id": t_id}})
        processed_count += 1
        
    return processed_count