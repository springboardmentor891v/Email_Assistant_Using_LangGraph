from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# SCOPES = [
#     "https://www.googleapis.com/auth/calendar"
# ]
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', "https://www.googleapis.com/auth/calendar"]
def get_calendar_service():
    creds = Credentials.from_authorized_user_file(
        "token.json", SCOPES
    )
    return build("calendar", "v3", credentials=creds)
