from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import os

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]


def get_calendar_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)

def create_event(subject: str):
    service = get_calendar_service()

    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(hours=1)

    event = {
        "summary": subject,
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Kolkata"},
    }

    service.events().insert(calendarId="primary", body=event).execute()
    print("📅 Calendar event created")
