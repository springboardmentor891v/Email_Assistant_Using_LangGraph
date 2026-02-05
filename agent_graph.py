from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from llm_utils import llm
from gmail_utils import send_email
from calendar_utils import check_availability, create_event
from memory_db import save_preference

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil import parser
import json, re


#STATE
class AgentState(TypedDict):
    sender: str
    subject: str
    body: str
    received_time: str
    action: Optional[str]
    meeting_date: Optional[str]
    meeting_time: Optional[str]
    meeting_duration: Optional[int]
    availability: Optional[str]
    draft_reply: Optional[str]
    approved_reply: Optional[str]


#HELPER
def extract_name(sender: str) -> str:
    name = sender.split("<")[0].strip()
    name = re.sub(r"[^A-Za-z ]", "", name)
    return name or "there"


#TRIAGE
def triage_node(state: AgentState):
    prompt = f"""
Classify this email into ONE:
respond / notify_human / ignore

Subject: {state['subject']}
Body: {state['body']}
"""
    decision = llm.invoke(prompt).content.lower()

    if "respond" in decision:
        state["action"] = "respond"
    elif "notify" in decision:
        state["action"] = "notify_human"
    else:
        state["action"] = "ignore"

    print("Triage:", state["action"])
    return state


#  EXTRACT DATE/TIME
def extract_datetime_node(state):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from dateutil import parser
    import json, re

    IST = ZoneInfo("Asia/Kolkata")

    prompt = f"""
Extract meeting date and time from this email.

Return JSON:
{{"date": "YYYY-MM-DD or null", "time": "HH:MM or null"}}

Email:
{state['body']}
"""
    response = llm.invoke(prompt).content.strip()

    try:
        data = json.loads(response)
        state["meeting_date"] = data.get("date")
        state["meeting_time"] = data.get("time")
    except:
        state["meeting_date"] = None
        state["meeting_time"] = None

    if not state["meeting_date"] or not state["meeting_time"]:
        try:
            dt = parser.parse(state["body"], fuzzy=True)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=IST)
            else:
                dt = dt.astimezone(IST)

            state["meeting_date"] = dt.strftime("%Y-%m-%d")
            state["meeting_time"] = dt.strftime("%H:%M")
        except:
            pass

    if state.get("meeting_date"):
        parsed_date = datetime.strptime(state["meeting_date"], "%Y-%m-%d")
        today = datetime.now(IST)

        if parsed_date.year < today.year:
            parsed_date = parsed_date.replace(year=today.year)

        if parsed_date.date() < today.date():
            parsed_date = parsed_date.replace(year=parsed_date.year + 1)

        state["meeting_date"] = parsed_date.strftime("%Y-%m-%d")

    duration_match = re.search(
        r"(\d+)\s*(hour|hr|hrs|hours|minute|minutes|min|mins)",
        state["body"],
        re.IGNORECASE
    )

    if duration_match:
        value = int(duration_match.group(1))
        unit = duration_match.group(2).lower()
        state["meeting_duration"] = value * 60 if "hour" in unit or "hr" in unit else value
    else:
        state["meeting_duration"] = 60

    return state



#CALENDAR CHECK
def calendar_node(state: AgentState, calendar_service):
    if state.get("meeting_date") and state.get("meeting_time"):
        ist = ZoneInfo("Asia/Kolkata")

        start_dt = datetime.strptime(
            f"{state['meeting_date']} {state['meeting_time']}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ist)

        duration = state.get("meeting_duration", 60)
        state["availability"] = check_availability(calendar_service, start_dt, duration)

    return state


#DRAFT
def draft_node(state: AgentState, USER_NAME: str):
    sender_name = extract_name(state["sender"])

    prompt = f"""
Write a professional reply.

Start with Dear {sender_name},

Email:
{state['body']}

Sign as:
Best regards,
{USER_NAME}
"""
    state["draft_reply"] = llm.invoke(prompt).content.strip()
    print("\nDraft:\n", state["draft_reply"])
    return state


#APPROVAL
def approval_node(state: AgentState):
    if not state.get("draft_reply"):
        return state

    choice = input("\nSend reply? (yes/edit/no): ")

    if choice == "yes":
        state["approved_reply"] = state["draft_reply"]
    elif choice == "edit":
        edited = input("Enter edited reply:\n")
        state["approved_reply"] = edited
        save_preference("tone_preference", edited[:150])
    else:
        state["approved_reply"] = None

    return state


# SEND + EVENT CREATION
def send_node(state, gmail_service, calendar_service):
    if state.get("approved_reply"):
        subject = state.get("subject") or "(No Subject)"
        send_email(gmail_service, state["sender"], subject, state["approved_reply"])
        print("Email sent")

        if (
            state.get("meeting_date")
            and state.get("meeting_time")
            and state.get("availability") == "free"
        ):
            ist = ZoneInfo("Asia/Kolkata")

            start_dt = datetime.strptime(
                f"{state['meeting_date']} {state['meeting_time']}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=ist)

            duration = state.get("meeting_duration", 60)

            link = create_event(calendar_service, subject, start_dt, duration)
            print(f"📅 Calendar event created for {duration} minutes:", link)

        elif state.get("availability") == "busy":
            print("Event not created because the time slot is busy.")

    return state


#BUILD GRAPH
def build_agent(gmail_service, calendar_service, USER_NAME):
    graph = StateGraph(AgentState)

    graph.add_node("triage", triage_node)
    graph.add_node("extract", extract_datetime_node)
    graph.add_node("calendar", lambda s: calendar_node(s, calendar_service))
    graph.add_node("draft", lambda s: draft_node(s, USER_NAME))
    graph.add_node("approve", approval_node)
    graph.add_node("send", lambda s: send_node(s, gmail_service, calendar_service))

    graph.set_entry_point("triage")

    graph.add_conditional_edges(
        "triage",
        lambda s: s["action"],
        {
            "respond": "extract",
            "notify_human": END,
            "ignore": END
        }
    )

    graph.add_edge("extract", "calendar")
    graph.add_edge("calendar", "draft")
    graph.add_edge("draft", "approve")
    graph.add_edge("approve", "send")
    graph.add_edge("send", END)

    return graph.compile()
