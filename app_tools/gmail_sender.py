# tools/gmail_sender.py

import base64
from email.mime.text import MIMEText

def send_reply(service, to, subject, reply_text, thread_id):
    message = MIMEText(reply_text)
    message['to'] = to
    message['subject'] = "Re: " + subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId='me',
        body={
            'raw': raw,
            'threadId': thread_id
        }
    ).execute()


def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()
