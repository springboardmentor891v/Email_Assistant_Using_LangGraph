import base64
from .gmail import get_gmail_service


def _decode_base64(data: str) -> str:
    """Decode base64url encoded email body safely."""
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _extract_body(payload: dict) -> str:
    """
    Extract plain text body from Gmail payload.
    Handles both single-part and multi-part emails.
    """
    # Case 1: Simple email (no parts)
    if "body" in payload and payload["body"].get("data"):
        return _decode_base64(payload["body"]["data"])

    # Case 2: Multipart email
    for part in payload.get("parts", []):
        mime = part.get("mimeType", "")
        if mime == "text/plain" and part.get("body", {}).get("data"):
            return _decode_base64(part["body"]["data"])

    return ""


def fetch_latest_email():
    """
    Fetch the latest real inbox email (not sent by me)
    and return all fields required by the agent.
    """
    service = get_gmail_service()

    # Get latest inbox email (exclude mails sent by you)
    results = service.users().messages().list(
        userId="me",
        q="is:inbox -from:me",
        maxResults=1
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return None

    msg_id = messages[0]["id"]

    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg["payload"].get("headers", [])

    def _get_header(name):
        for h in headers:
            if h["name"].lower() == name.lower():
                return h["value"]
        return ""

    subject = _get_header("Subject")
    sender = _get_header("From")

    body = _extract_body(msg["payload"])

    return {
        "id": msg_id,
        "threadId": msg["threadId"],
        "sender": sender,
        "subject": subject,
        "body": body.strip(),
    }
