"""
Gmail Service - OAuth2 Authentication and API Client
"""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """
    Authenticate and return Gmail API service client.
    
    Uses credentials.json for first-time OAuth flow.
    Saves token.json for subsequent runs.
    
    Returns:
        Gmail API service object
    """
    creds = None
    
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # Run OAuth flow with credentials.json
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found! "
                    "Get it from https://console.cloud.google.com/"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build and return Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service


if __name__ == "__main__":
    # Test authentication
    try:
        service = get_gmail_service()
        # Test API call
        results = service.users().messages().list(
            userId='me',
            maxResults=1
        ).execute()
        print("✅ Gmail API authentication successful!")
        print(f"Found {results.get('resultSizeEstimate', 0)} messages in mailbox")
    except Exception as e:
        print(f"❌ Error: {e}")
