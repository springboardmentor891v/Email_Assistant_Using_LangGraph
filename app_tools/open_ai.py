# tools/openai_agent.py

import os
import json
import re
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from memory.memory_store import get_preference, get_feedback

# Using Groq for lightning-fast inference - NO quota limits!
# Groq is extremely fast and has a generous free tier
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Latest available Groq model
    temperature=0.3,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)


def extract_json(text: str):
    """
    Safely extract the first JSON object from LLM output.
    Returns dict or None.
    """
    if not text:
        return None

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def extract_and_check_event(email_body: str):
    """
    MERGED FUNCTION: Combines event detection + extraction in ONE LLM call.
    Reduces API calls from 2 to 1.
    Returns: (should_create: bool, details: dict | None)
    """
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    Does this email require creating a calendar event?
    If YES, extract the details. If NO, return null for details.

    Today's date is {today}

    Rules for event extraction:
    - Resolve relative dates like "tomorrow" using today's date
    - Convert informal times like "4pm" to 24-hour format
    - Assume timezone: Asia/Kolkata
    - If duration is missing, assume 1 hour

    Email:
    {email_body}

    Return ONLY valid JSON in this exact format:
    {{
    "should_create_event": true/false,
    "title": "string or null",
    "description": "string or null",
    "start_datetime": "YYYY-MM-DDTHH:MM:SS or null",
    "end_datetime": "YYYY-MM-DDTHH:MM:SS or null"
    }}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()
    result = extract_json(raw)

    if result:
        should_create = result.get("should_create_event", False)
        details = {
            "title": result.get("title"),
            "description": result.get("description"),
            "start_datetime": result.get("start_datetime"),
            "end_datetime": result.get("end_datetime")
        } if should_create else None
        return should_create, details
    
    return False, None


def generate_reply_unified(subject, sender, body, alternative_slots=None):
    """
    MERGED FUNCTION: Handles both normal and conflict cases.
    Reduces API calls from 2 to 1 when conflict detected.
    If alternative_slots provided, LLM will suggest those times.
    """
    tone = get_feedback("tone") or "professional"
    verbosity = get_feedback("verbosity") or "medium"
    
    slots_context = ""
    if alternative_slots:
        slots_str = ", ".join(alternative_slots)
        slots_context = f"\n\nIMPORTANT: There is a scheduling conflict. Suggest these alternative meeting times: {slots_str}"

    prompt = f"""
    You are an email assistant.
    your name is Premendar Reddy.
    Tone: {tone}
    Verbosity: {verbosity}

    write a reply to the following email.

    Subject: {subject}
    From: {sender}

    Email:
    {body}{slots_context}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def infer_preferences_from_edit(original_reply, edited_reply):
    """
    Infers user preferences by comparing original and edited replies.
    """
    prompt = f"""
Compare the original reply and the edited reply.

Original reply:
{original_reply}

Edited reply:
{edited_reply}

Infer user preferences.
Return ONLY JSON.

Possible keys:
- tone: friendly | formal | concise
- verbosity: short | medium | long

JSON format:
{{
  "tone": "...",
  "verbosity": "..."
}}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


# ============================================================
# Backward compatibility: deprecated functions
# ============================================================
def generate_reply(subject, sender, body):
    """DEPRECATED: Use generate_reply_unified instead."""
    return generate_reply_unified(subject, sender, body)


def llm_should_create_event(body: str) -> bool:
    """DEPRECATED: Use extract_and_check_event instead."""
    should_create, _ = extract_and_check_event(body)
    return should_create


def extract_event_details(email_body: str):
    """DEPRECATED: Use extract_and_check_event instead."""
    _, details = extract_and_check_event(email_body)
    return details


def generate_alternative_slots_reply(email_body, slots):
    """DEPRECATED: Use generate_reply_unified with alternative_slots parameter."""
    return generate_reply_unified("", "", email_body, alternative_slots=slots)
