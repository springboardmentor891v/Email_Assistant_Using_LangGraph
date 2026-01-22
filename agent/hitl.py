# agent/hitl_agent.py

from auth.gmail_auth import get_gmail_service
from tools.gmail_reader import get_unread_emails, read_email
from tools.open_ai import generate_reply
from tools.gmail_sender import send_reply, mark_as_read

def run_hitl_agent():
    service = get_gmail_service()
    messages = get_unread_emails(service)

    for msg in messages:
        msg_id = msg['id']
        thread_id = msg['threadId']

        subject, sender, body = read_email(service, msg_id)

        print("\n" + "="*60)
        print("📧 SUBJECT:", subject)
        print("👤 FROM:", sender)
        print("📝 BODY:\n", body[:500])
        print("="*60)

        if input("Reply to this email? (y/n): ").lower() != 'y':
            continue

        reply = generate_reply(subject, sender, body)
        print("\n🤖 Generated Reply:\n", reply)

        decision = input("Approve reply? (y / n / edit): ").lower()

        if decision == 'edit':
            reply = input("Enter edited reply:\n")

        if decision in ['y', 'edit']:
            send_reply(service, sender, subject, reply, thread_id)
            mark_as_read(service, msg_id)
            print("✅ Reply sent and marked as read")
