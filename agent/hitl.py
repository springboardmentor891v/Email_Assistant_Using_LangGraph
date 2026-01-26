from auth.gmail_auth import get_gmail_service
from app_tools.gmail_reader import get_unread_emails, read_email
from app_tools.open_ai import generate_reply, llm_should_create_event, extract_event_details
from app_tools.gmail_sender import send_reply, mark_as_read
from app_tools.calender_tools import create_event, has_conflict
from memory.memory_store import init_db, save_preference
from auth.calendar_auth import get_calendar_service



def triage(body):
    b = body.lower()
    if "otp" in b or "verification" in b:
        return "ignore"
    return "respond"


def run_hitl_agent():
    init_db()
    service = get_gmail_service()
    calendar_service = get_calendar_service()
    emails = get_unread_emails(service)

    for e in emails:
        msg_id = e["id"]
        thread_id = e["threadId"]

        subject, sender, body = read_email(service, msg_id)

        print("\n==============================")
        print("SUBJECT:", subject)
        print(body[:500])
        print("==============================")

        if triage(body) == "ignore":
            mark_as_read(service, msg_id)
            print("Ignored by triage")
            continue

        if input("Reply? (y/n): ").lower() not in ["y", "yes"]:
            continue

        reply = generate_reply(subject, sender, body)
        print("\nDraft:\n", reply)

        choice = input("Approve / edit / skip: ").lower()

        if choice == "edit":
            reply = input("Enter edited reply:\n")
            save_preference("tone", "friendly")

        if choice not in ["approve", "edit", "y"]:
            print("Reply skipped")
            continue


        # ---------- CALENDAR LOGIC (AFTER REPLY) ----------
        should_event = llm_should_create_event(body)
        print("TRIGGER:", should_event)
        print("⚠️ ABOUT TO ASK CALENDAR APPROVAL-1")
        if should_event:
            details = extract_event_details(body)
            print("EXTRACTED DETAILS:", details)
            print("⚠️ ABOUT TO ASK CALENDAR APPROVAL-2")
            if details:
                print("⚠️ ABOUT TO ASK CALENDAR APPROVAL-3")
                print("\n📅 Proposed Calendar Event:")
                print("Title:", details["title"])
                print("Description:", details["description"])
                print("Start:", details["start_datetime"])
                print("End:", details["end_datetime"])

                if input("Approve calendar event? (y/n): ").lower() == "y":

                    conflict = has_conflict(
                        calendar_service,
                        details["start_datetime"],
                        details["end_datetime"]
                    )

                    if conflict:
                        print("⚠️ This event overlaps with an existing calendar event.")
                        override = input("Create anyway? (y/n): ").lower()
                        if override != "y":
                            print("Calendar event skipped due to conflict.")
                            continue

                    create_event(
                        calendar_service,
                        details["title"],
                        details["description"],
                        details["start_datetime"],
                        details["end_datetime"]
                    )



        # ---------- SEND REPLY ----------
        send_reply(service, sender, subject, reply, thread_id)
        print("Reply sent")
        mark_as_read(service, msg_id)

