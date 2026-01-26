from googleapiclient.discovery import build
from src.gemini import llm_call
import datetime
from src.auth import authenticate_google

creds = authenticate_google()
calendar_service = build('calendar', 'v3', credentials=creds)
gmail_service = build('gmail', 'v1', credentials=creds)

# ---------------- Calendar Tools
# Calendar Tools
import datetime

def ensure_timezone(iso_time):
    """Helper to ensure time string ends with Z if no offset exists."""
    if not iso_time.endswith('Z') and '+' not in iso_time[-6:]:
        return iso_time + 'Z'
    return iso_time

def check_availability(service, start_time_iso):
    """
    Checks availability and returns the conflicting event object if busy.
    """
    # 1. Fix Timezone (Prevents 400 Error)
    start_time_iso = ensure_timezone(start_time_iso)

    # 2. Calculate End Time
    start = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
    end = start + datetime.timedelta(hours=1)
    end_time_iso = end.isoformat()
    
    # Ensure end time also has Z if needed
    end_time_iso = ensure_timezone(end_time_iso)

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time_iso,
            timeMax=end_time_iso,
            singleEvents=True
        ).execute()

        events = events_result.get('items', [])
        
        # 3. Return Dictionary (Required for 'Replace' logic)
        if events:
            return {"status": "BUSY", "event": events[0]}
        
        return {"status": "FREE", "event": None}
        
    except Exception as e:
        print(f"Calendar API Check Error: {e}")
        return {"status": "ERROR", "event": None}

def add_event(service, summary, start_time_iso):
    """Adds an event to the primary calendar."""
    # 1. Fix Timezone
    start_time_iso = ensure_timezone(start_time_iso)
    
    start = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
    end = start + datetime.timedelta(hours=1)
    end_time_iso = end.isoformat()
    
    # Ensure end time also has Z
    end_time_iso = ensure_timezone(end_time_iso)

    event_body = {
        'summary': summary,
        'start': {'dateTime': start_time_iso},
        'end': {'dateTime': end_time_iso}
    }
    
    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return f"Success: Event created at {event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating event: {e}"

def delete_event(service, event_id):
    """Deletes an event by ID."""
    try:
        # Fixed typo: .delet -> .delete
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"🗑️ Deleted conflicting event (ID: {event_id})")
        return True
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False


# -------------------- Email tools
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

def search_gmail(service, query, get_all=False, max_results=5):
    """
    Search Gmail using pagination to retrieve all matching messages.
    """
    full_emails = []
    next_page_token = None
    
    try:
        while True:
            # Call the API with the nextPageToken if it exists
            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=500 if get_all else max_results,
                pageToken=next_page_token
            ).execute()

            messages = results.get("messages", [])
            
            # Fetch full content for this batch
            for msg in messages:
                message = service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format='full'
                ).execute()
                full_emails.append(message)

            # Check if we should stop
            next_page_token = results.get('nextPageToken')
            
            # Stop if:
            # 1. No more pages exist
            # 2. We only wanted a specific number (get_all=False)
            if not next_page_token or not get_all:
                break

        return full_emails, len(full_emails)
        
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    
import json
from datetime import date

def query_gmail_assistant(user_question):
    today = date.today().strftime("%Y/%m/%d")

    prompt = f"""
    You are an expert Translator for the Gmail API.
    Your goal is to convert a user's natural language question into a Gmail search query (parameter 'q').

    ### CONTEXT:
    - Today's Date: {today}
    - User: Sanjay Sanapala

    ### GMAIL QUERY SYNTAX CHEATSHEET:
    - Unread emails: "is:unread"
    - From specific person: "from:name@example.com" or "from:Name"
    - Subject contains: "subject:(meeting)"
    - Date range: "after:2024/01/01 before:2024/01/31"
    - Labels: "label:Work", "label:Updates"
    - Categories: "category:primary", "category:social", "category:promotions"
    - Exact phrase: "\"exact phrase\""

    ### EXAMPLES:
    User: "How many unread emails do I have?"
    Output: {{"query": "is:unread", "intention": "count"}}

    User: "Show me the latest email from Sanjay."
    Output: {{"query": "from:Sanjay", "intention": "list"}}

    User: "Any emails about the internship in the last 2 days?"
    Output: {{"query": "internship after:{today}", "intention": "list"}}

    ### INPUT:
    User: "{user_question}"

    ### OUTPUT (JSON ONLY):
    Return valid JSON with keys: "query" (the gmail search string) and "intention" (either "count" or "list").
    """

    response = llm_call(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"query": "", "intention": "error"}
    
def ask_gmail(service, query):
    print(f"User asking: '{query}'")

    res = query_gmail_assistant(query)
    gmail_query = res.get("query")
    intention = res.get("intention")

    print(f"Generated Query: '{gmail_query}' (Intention: {intention})")

    if not gmail_query:
        return "Sorry, I couldn't understand how to search for that"
    
    emails, count = search_gmail(service, gmail_query, max_results=500)

    if intention == "count":
        return f"I found approximately {count} emails matching your request"
    elif intention == "list":
        if not emails:
            return "No emails found matching that criteria."
        
        final_prompt = f"User asked: '{query}'.\nHere are the email details found:\n"

        for email in emails:
            sender, subject, body = extract_email_parts(email)
        
        final_prompt += "\n Answer the user's question naturally based on these emails."
        return llm_call(final_prompt)
    
# response = ask_gmail(service, "How many unread emails are there")
# print(response)