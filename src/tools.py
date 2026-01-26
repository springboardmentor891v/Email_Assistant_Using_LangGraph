from googleapiclient.discovery import build
import datetime
from src.auth import authenticate_google

creds = authenticate_google()
calendar_service = build('calendar', 'v3', credentials=creds)
gmail_service = build('gmail', 'v1', credentials=creds)

def create_calendar_event(summary, start_time_iso, end_time_iso):
    """
    Create a new calendar event.
    start_time_iso format example: '2026-01-28T09:00:00-07:00'
    """
    event = {
        'summary': summary,
        'start': {'dateTime': start_time_iso},
        'end': {'dateTime': end_time_iso},
    }
    event = calendar_service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {event.get('htmlLink')}"

def fetch_recent_emails(service, max_results=5):
    """
    Fetch the recent emails.
    """
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    full_email_objects = []

    for msg in messages:
        message = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()
        
        full_email_objects.append(message) 

    return full_email_objects

import base64
from typing import TypedDict, List, Dict, Any

def extract_body(payload: dict) -> str:
    """
    Extract the body from the email returned by gmail
    """
    body = ""

    if "data" in payload.get("body", {}):
        body = payload["body"]["data"]

    elif "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                body = part["body"]["data"]
                break

    if body:
        return base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")

    return ""


def extract_email_parts(message: dict):
    """
    Extract the email parts like sender, subject and body from returned value by gmail
    """
    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    subject = ""
    sender = ""

    for h in headers:
        name = h.get("name", "").lower()
        if name == "subject":
            subject = h.get("value", "")
        elif name == "from":
            sender = h.get("value", "")

    body = extract_body(payload)

    return sender, subject, body

def format_email_for_llm(sender, subject, body):
    return f"Sender: {sender}\nSubject: {subject}\n\nBody:\n{body}\n".strip()

def search_gmail(service, query, max_results=5):
    """Search Gmail using the 'q' parameter."""
    try:
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults = max_results
        ).execute()

        messages = results.get("messages", [])

        if "resultSizeEstimate" in results and max_results == 1 and not messages:
            return [], results.get("resultSizeEstimate", 0)
        
        full_emails = []
        for msg in messages:
            message = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format='full'
            ).execute()
            full_emails.append(message)

        return full_emails, len(messages)
    except Exception as e:
        print(f"Error: {e}")
        return [], 0