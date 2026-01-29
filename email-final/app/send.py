from .state import EmailState
from .gmail import send_email

def send_if_approved(state: EmailState) -> EmailState:
    """
    Send the email reply if human approved it.
    """

    # ✅ Only send if approved
    if state.get("human_decision") != "approve":
        return state

    # ✅ Always read reply from state
    reply_text = state.get("reply", "")

    if not reply_text:
        print("⚠️ No reply text found. Skipping send.")
        return state

    send_email(
        to=state["sender"],
        subject=state.get("subject", ""),
        body=reply_text,
        thread_id=state.get("threadId")  # may be None for new email
    )

    print("📧 Reply sent in same thread")

    # IMPORTANT: do NOT overwrite reply
    state["reply"] = reply_text

    return state

