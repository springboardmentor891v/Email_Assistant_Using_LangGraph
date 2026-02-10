import os
import sqlite3
import base64
from email.message import EmailMessage

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from typing import TypedDict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



class State(TypedDict):
    user_input: str
    draft: str
    preferred_name: str



memory = MemorySaver()





def draft_email(state: State):
    name = state.get("preferred_name", "Bob")
    draft = f"Hello {name},\n\nThis is a test email from my LangGraph agent.\n\nRegards"
    return {"draft": draft}


def save_preferred_name(state: State):
    text = state["draft"]
    if "Robert" in text:
        return {"preferred_name": "Robert"}
    return {}



graph = StateGraph(State)
graph.add_node("draft", draft_email)
graph.add_node("learn", save_preferred_name)

graph.set_entry_point("draft")
graph.add_edge("draft", "learn")
graph.set_finish_point("learn")

app = graph.compile(checkpointer=memory)


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_real_email(to_email, subject, body):
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to_email
    message["From"] = "me"
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_message = {"raw": encoded_message}

    service.users().messages().send(
        userId="me",
        body=send_message
    ).execute()

    print("✅ Email sent successfully!")


print("---- First Run ----")

result1 = app.invoke(
    {"user_input": "Email Bob"},
    config={"configurable": {"thread_id": "user1"}}
)

print(result1["draft"])

edited_state = {
    "draft": result1["draft"].replace("Bob", "Robert")
}

app.invoke(
    edited_state,
    config={"configurable": {"thread_id": "user1"}}
)


print("\n---- Second Run ----")

result2 = app.invoke(
    {"user_input": "Email Bob"},
    config={"configurable": {"thread_id": "user1"}}
)

print(result2["draft"])



send_real_email(
    to_email="YOUR_EMAIL@gmail.com",  
    subject="LangGraph Email Agent Test",
    body=result2["draft"]
)
