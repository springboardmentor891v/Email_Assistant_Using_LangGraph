from gmail_utils import authorize_google_services, get_email_content, get_user_name
from agent_graph import build_agent, AgentState
from memory_db import init_db, mark_processed
from evaluation import run_with_tracing

print(" Starting AI Email Agent...\n")

# INIT MEMORY
init_db()

#GOOGLE LOGIN
gmail_service, calendar_service = authorize_google_services()
USER_NAME = get_user_name(gmail_service)

agent = build_agent(gmail_service, calendar_service, USER_NAME)

# FETCH EMAILS
results = gmail_service.users().messages().list(
    userId='me',
    labelIds=['UNREAD'],
    maxResults=5
).execute()

messages = results.get('messages', [])

if not messages:
    print(" No unread emails found.")
    exit()

# PROCESS EMAILS
for msg in messages:
    email_id = msg['id']

    subject, sender, body, received_time = get_email_content(gmail_service, email_id)

    print("\n" + "=" * 60)
    print("From:", sender)
    print("Subject:", subject)
    print("Received:", received_time)
    print("=" * 60)

    state = AgentState(
        sender=sender,
        subject=subject,
        body=body,
        received_time=received_time,
        action=None,
        meeting_date=None,
        meeting_time=None,
        meeting_duration=None,
        availability=None,
        suggested_slots=None,
        draft_reply=None,
        approved_reply=None
    )

    final_state = run_with_tracing(agent, state)
    if final_state.get("approved_reply"):
        mark_processed(email_id, sender, subject)
        print(" Interaction stored in memory.")

print("\n Agent run complete.\n")