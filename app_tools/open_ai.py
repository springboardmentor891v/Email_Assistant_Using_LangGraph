# tools/openai_agent.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from memory.memory_store import get_preference
import json
from datetime import datetime

today = datetime.utcnow().date()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

def generate_reply(subject, sender, body):
    tone = get_preference("tone") or "professional"

    prompt = f"""
You are an email assistant.
Write a {tone} reply.

Subject: {subject}
From: {sender}

Email:
{body}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content




def llm_should_create_event(body: str) -> bool:
    prompt = f"""
    Does this email require creating a calendar event?
    Answer only YES or NO.

    Email:
    {body}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return "yes" in response.content.lower()




def extract_event_details(body: str):
    prompt = f"""
Extract calendar event details from the email below.

If information is missing, make a reasonable guess.
todays date is {today}.

Return ONLY valid JSON.
Do NOT add explanations, markdown, or extra text.

Return ONLY valid JSON with these keys:
- title
- description
- start_datetime (ISO 8601) if any
- end_datetime (ISO 8601) if any

Email:
{body}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except Exception:
        return None
