import os, re, base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timezone

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]

def authorize_google_services():
    creds = None
    if os.path.isfile('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds), build('calendar', 'v3', credentials=creds)


def get_user_name(gmail_service):
    profile = gmail_service.users().getProfile(userId='me').execute()
    email = profile.get("emailAddress", "")
    name = re.sub(r'\d+', '', email.split("@")[0]).replace('.', ' ').replace('_', ' ')
    return name.title()


def get_email_content(gmail_service, msg_id):
    msg = gmail_service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    subject = sender = ""
    for h in msg['payload']['headers']:
        if h['name'] == 'Subject': subject = h['value']
        if h['name'] == 'From': sender = h['value']

    body = ""
    for part in msg['payload'].get('parts', []):
        if part.get('mimeType') == 'text/plain':
            body = base64.urlsafe_b64decode(part['body']['data']).decode(errors='ignore')

    ts = int(msg['internalDate']) / 1000
    received = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%d %B %Y, %I:%M %p")

    return subject, sender, body, received


def send_email(gmail_service, to_email, subject, text):
    msg = MIMEText(text)
    msg['to'] = to_email
    msg['subject'] = "Re: " + (subject or "(No Subject)")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_service.users().messages().send(userId='me', body={'raw': raw}).execute()
