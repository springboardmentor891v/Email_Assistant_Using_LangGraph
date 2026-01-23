"""
Gmail Email Tools - Real Gmail API Integration
"""
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.gmail_service import get_gmail_service


def list_unread_emails(max_results: int = 10) -> List[str]:
    """
    List unread emails from inbox.
    
    Args:
        max_results: Maximum number of emails to fetch
        
    Returns:
        List of message IDs
    """
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return [msg['id'] for msg in messages]
    except Exception as e:
        print(f"Error listing emails: {e}")
        return []


def read_email(message_id: str) -> Dict[str, str]:
    """
    Read a specific email by message ID.
    
    Args:
        message_id: Gmail message ID
        
    Returns:
        Dict with 'id', 'from', 'subject', 'date', 'body'
    """
    try:
        service = get_gmail_service()
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = message['payload']['headers']
        email_data = {'id': message_id}
        
        for header in headers:
            name = header['name'].lower()
            if name == 'from':
                email_data['from'] = header['value']
            elif name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'date':
                email_data['date'] = header['value']
        
        # Extract body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(
                message['payload']['body']['data']
            ).decode('utf-8')
        
        email_data['body'] = body
        return email_data
        
    except Exception as e:
        print(f"Error reading email {message_id}: {e}")
        return {}


def send_email(to: str, subject: str, body: str) -> bool:
    """
    Send an email via Gmail API.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        service = get_gmail_service()
        
        # Create MIME message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')
        
        # Send
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ Email sent to {to}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def mark_as_read(message_id: str) -> bool:
    """
    Mark an email as read.
    
    Args:
        message_id: Gmail message ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error marking email as read: {e}")
        return False


# Export for LangChain tool wrapping if needed
ALL_EMAIL_TOOLS = []


if __name__ == "__main__":
    # Test email tools
    print("Testing Gmail API...")
    
    # List unread emails
    print("\n📬 Unread emails:")
    unread = list_unread_emails(max_results=5)
    print(f"Found {len(unread)} unread emails")
    
    # Read first email
    if unread:
        print(f"\n📖 Reading email {unread[0]}:")
        email = read_email(unread[0])
        print(f"From: {email.get('from')}")
        print(f"Subject: {email.get('subject')}")
        print(f"Body preview: {email.get('body', '')[:100]}...")
