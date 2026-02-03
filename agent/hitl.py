from auth.gmail_auth import get_gmail_service
from auth.calendar_auth import get_calendar_service

from app_tools.gmail_reader import get_unread_emails, read_email
from app_tools.gmail_sender import send_reply, mark_as_read

from app_tools.open_ai import (
    generate_reply_unified,
    extract_and_check_event,
    infer_preferences_from_edit
)

from app_tools.calender_tools import (
    create_event,
    has_conflict,
    suggest_free_slots
)

from memory.memory_store import (
    init_db,
    save_feedback
)

from datetime import datetime, timezone
import json


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def normalize(dt_str: str) -> str:
    """
    Convert ISO datetime string to RFC3339 UTC (required by Google Calendar).
    """
    if dt_str.endswith("Z"):
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def triage(body: str) -> str:
    b = body.lower()
    if "otp" in b or "verification" in b:
        return "ignore"
    return "respond"


def parse_user_choice(user_input: str) -> str:
    """
    Parse user input and return normalized choice.
    Supports shortcuts: 
    - Approve: 'approve', 'a', 'yes', 'y'
    - Edit: 'edit', 'e'
    - Skip: 'skip', 's', 'n', 'no'
    """
    choice = user_input.lower().strip()
    
    # Approve shortcuts
    if choice in ["approve", "a", "yes", "y"]:
        return "approve"
    
    # Edit shortcuts
    if choice in ["edit", "e"]:
        return "edit"
    
    # Skip shortcuts
    if choice in ["skip", "s", "n", "no"]:
        return "skip"
    
    return "skip"  # Default to skip for unknown input


# --------------------------------------------------
# Main HITL Agent
# --------------------------------------------------

def run_hitl_agent():
    init_db()

    gmail_service = get_gmail_service()
    calendar_service = get_calendar_service()

    emails = get_unread_emails(gmail_service)

    for e in emails:
        msg_id = e["id"]
        thread_id = e["threadId"]

        subject, sender, body = read_email(gmail_service, msg_id)

        print("\n==============================")
        print("SUBJECT:", subject)
        print(body[:500])
        print("==============================")

        # ---------- TRIAGE ----------
        if triage(body) == "ignore":
            mark_as_read(gmail_service, msg_id)
            print("Ignored by triage")
            continue

        if input("Reply? (y/n): ").lower() not in ["y", "yes"]:
            continue

        # --------------------------------------------------
        # STEP 1: Extract event info and decide reply strategy (MERGED 2 CALLS → 1)
        # --------------------------------------------------

        should_event, details = extract_and_check_event(body)
        
        reply = None
        conflict = False

        if should_event and details:
            print("📅 EVENT DETECTED:", details.get("title"))
            print("EXTRACTED DETAILS:", details)

            start = normalize(details["start_datetime"])
            end = normalize(details["end_datetime"])

            conflict = has_conflict(calendar_service, start, end)

            # ---------- CONFLICT → SUGGEST ALTERNATIVES ----------
            if conflict:
                print("⚠️ Calendar conflict detected")

                date = details["start_datetime"].split("T")[0]
                free_slots = suggest_free_slots(calendar_service, date)

                reply = generate_reply_unified(
                    subject,
                    sender,
                    body,
                    alternative_slots=free_slots
                )
            else:
                reply = generate_reply_unified(subject, sender, body)
        else:
            reply = generate_reply_unified(subject, sender, body)

        # --------------------------------------------------
        # STEP 2: Human-in-the-loop approval
        # --------------------------------------------------

        print("\nDraft:\n", reply)
        print("\n📝 Options: (A)pprove / (E)dit / (S)kip")
        choice = parse_user_choice(input("Your choice: "))

        # ---------- LEARNING FROM FEEDBACK ----------
        if choice == "edit":
            edited_reply = input("Enter edited reply:\n")

            prefs_json = infer_preferences_from_edit(reply, edited_reply)
            try:
                prefs = json.loads(prefs_json)
                for k, v in prefs.items():
                    save_feedback(k, v)
            except Exception:
                pass

            reply = edited_reply

        if choice != "approve":
            print("Reply skipped")
            continue

        # --------------------------------------------------
        # STEP 3: Send reply
        # --------------------------------------------------

        send_reply(
            gmail_service,
            sender,
            subject,
            reply,
            thread_id
        )
        mark_as_read(gmail_service, msg_id)
        print("Reply sent")

        # --------------------------------------------------
        # STEP 4: Create calendar event ONLY if no conflict
        # --------------------------------------------------

        if should_event and details and not conflict:
            print("📅 Creating calendar event")

            create_event(
                calendar_service,
                details["title"],
                details["description"],
                details["start_datetime"],
                details["end_datetime"]
            )
