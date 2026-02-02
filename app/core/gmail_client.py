import os
import base64
from typing import TypedDict, Annotated, List, Literal
from email.mime.text import MIMEText

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Google API Imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError
import pickle
import datetime
import base64
from email.mime.text import MIMEText

# 1. SETUP GMAIL AUTHENTICATION
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]


def get_gmail_service():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials1.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    gmail_service = build('gmail', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)

    return gmail_service, calendar_service


service, calendar_service = get_gmail_service()

def read_inbox(service, max_results=5):
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['From', 'Subject']
        ).execute()

        headers = message['payload']['headers']
        email_data = {}

        for h in headers:
            email_data[h['name']] = h['value']

        print("\n📩 New Email")
        print("From:", email_data.get('From'))
        print("Subject:", email_data.get('Subject'))

# FETCH Unread Emails

def fetch_unread_emails(service, max_results=5):
    return service.users().messages().list(
        userId="me",
        labelIds=["UNREAD"],
        maxResults=max_results
    ).execute().get("messages", [])

# Extarct Emails

def extract_email(service, msg_id):
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg["payload"]["headers"]
    subject = sender = ""

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        elif h["name"] == "From":
            sender = h["value"]

    body = ""
    payload = msg["payload"]

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode()
    else:
        data = payload["body"].get("data")
        if data:
            body = base64.urlsafe_b64decode(data).decode()

    return subject, sender, body, msg["threadId"]

import re

# Clean Email body


def clean_email_body(body: str) -> str:
    # Remove markdown JSON blocks
    body = re.sub(r"```json[\s\S]*?```", "", body, flags=re.IGNORECASE)

    # Remove quoted replies (Gmail style)
    body = re.split(r"\nOn .* wrote:", body)[0]

    # Remove lines starting with >
    body = "\n".join(
        line for line in body.splitlines()
        if not line.strip().startswith(">")
    )

    return body.strip()

# Send Reply
def send_reply(service, to, subject, reply, thread_id):
    message = MIMEText(reply)
    message["to"] = to
    message["subject"] = "Re: " + subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": thread_id}
    ).execute()

# mark as read
def mark_read(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()
