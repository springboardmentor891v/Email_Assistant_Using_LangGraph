from app.agent.graph import build_email_graph
from app.core.gmail_client import clean_email_body, extract_email, fetch_unread_emails, mark_read


def run_email_assistant(service, calendar_service, user_prompt, max_results=5):
    app = build_email_graph(user_prompt, service, calendar_service)
    emails = fetch_unread_emails(service, max_results=max_results)

    if not emails:
        print("📭 No unread emails found.")
        return

    print(f"\n📬 Total unread emails: {len(emails)}")

    for i, msg in enumerate(emails, start=1):
        print("\n" + "=" * 70)
        print(f"📧 Processing email {i}/{len(emails)}")

        subject, sender, body, thread_id = extract_email(service, msg["id"])
        body = clean_email_body(body)

        print(f"From   : {sender}")
        print(f"Subject: {subject}")
        print("\n📨 Email Body")
        print("-" * 60)
        print(body.strip())
        print("-" * 60)

        state = {
            "subject": subject,
            "sender": sender,
            "body": body,
            "thread_id": thread_id,
            "decision": {},
            "final_reply": None
        }

        try:
            result = app.invoke(state)

            if result.get("final_reply") or result.get("decision", {}).get("action") != "ignore":
                mark_read(service, msg["id"])
                print("📩 Email marked as read")
            else:
                print("⏸️ Email left unread")

        except Exception as e:
            print(f"❌ Graph failed: {e}")
