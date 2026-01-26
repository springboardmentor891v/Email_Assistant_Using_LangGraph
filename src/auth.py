# Setting up Gmail
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 1. SETUP Google AUTHENTICATION
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENTS_DIR = os.path.join(BASE_DIR, "contents")
CRED_PATH = os.path.join(CONTENTS_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CONTENTS_DIR, "token.json")


def authenticate_google():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds

service = build('gmail', 'v1', credentials=authenticate_google())

# Check if gmail is connected
# profile = service.users().getProfile(userId='me').execute()
# print("Email:", profile["emailAddress"])