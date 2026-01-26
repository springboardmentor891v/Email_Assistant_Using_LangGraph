from src.tools import fetch_recent_emails, extract_body, extract_email_parts, format_email_for_llm
from src.agent import traige_email, create_draft_reply
from src.auth import authenticate_google
from googleapiclient.discovery import build

creds = authenticate_google()
calendar_service = build('calendar', 'v3', credentials=creds)
gmail_service = build('gmail', 'v1', credentials=creds)

if __name__ == "__main__":
    messages = fetch_recent_emails(gmail_service, 1)

    for msg in messages:
        sender, subject, body = extract_email_parts(msg)

        mail_text = format_email_for_llm(sender, subject, body)

        decision = traige_email(mail_text).strip()
        decision = decision.replace('"', '').replace("'", "").strip()
        
        print(f"Decision: {decision}")

        if decision == "IGNORE":
            print("Mail Ignored")
            
        elif decision == "NOTIFY":
            print(f"Notification: {subject}")
            
        elif decision == "RESPOND":
            create_draft_reply(gmail_service, sender, subject, body)