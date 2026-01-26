from src.tools import ask_gmail
from src.auth import get_gmail_service, get_calendar_service
from googleapiclient.discovery import build

calendar_service = get_calendar_service()
gmail_service = get_gmail_service()

# if __name__ == "__main__":
#     messages = fetch_recent_emails(gmail_service, 1)

#     for msg in messages:
#         sender, subject, body = extract_email_parts(msg)

#         mail_text = format_email_for_llm(sender, subject, body)

#         decision = traige_email(mail_text).strip()
#         decision = decision.replace('"', '').replace("'", "").strip()
        
#         print(f"Decision: {decision}")

#         if decision == "IGNORE":
#             print("Mail Ignored")
            
#         elif decision == "NOTIFY":
#             print(f"Notification: {subject}")
            
#         elif decision == "RESPOND":
#             create_draft_reply(gmail_service, sender, subject, body)


response = ask_gmail(gmail_service, "How many unread emails are there")
print(response)