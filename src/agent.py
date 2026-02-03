import json
from src.gemini import llm_call
# from src.groq_llm import llm_call_1
from src.tools import add_event, delete_event, send_email, check_availability
from src.db import MemoryManager
from datetime import datetime
from langsmith import traceable

memory = MemoryManager()

def learn_from_feedback(feedback_text):
    """
    Uses LLM to distill raw feedback into a reusable rule.
    """
    prompt = f"""
    Analyze this user feedback: "{feedback_text}"
    
    Does this contain a general preference or rule for future emails?
    If yes, extract it as a short Key-Value pair.
    
    Examples:
    - "Don't use 'Dear' anymore" -> Key: "Greeting", Value: "Do not use 'Dear'"
    - "I'm always busy on Mondays" -> Key: "Schedule", Value: "Busy on Mondays"
    
    Return ONLY valid JSON: {{ "key": "...", "value": "..." }}
    If no general rule exists, return {{ "key": "NONE", "value": "" }}
    """
    
    try:
        # We assume llm_call is available or use self.client.generate_content
        response = llm_call(prompt) 
        data = json.loads(response.replace("```json", "").replace("```", ""))
        
        if data["key"] != "NONE":
            memory.save_preference(data["key"], data["value"])
            return f"Learned: {data['key']} -> {data['value']}"
    except Exception as e:
        print(f"Learning failed: {e}")
    return ""

@traceable(name="triage")
def traige_email(email_text: str) -> str:
    prompt = f"""
    You are an expert AI Executive Assistant.
    Your goal is to triage incoming emails into specific category

    ### CATEGORY DEFINITIONS:
    1. **IGNORE**: Automated newsletters, marketing, receipts, system logs, or spam.
    2. **NOTIFY**: informational emails where NO reply is expected (e.g., shipping updates, "FYI" memos, broad company announcements, "OTP"s).
    3. **RESPOND**: Emails that require a reply or action. This INCLUDES:
    - Invitations (Parties, Weddings, Meetings) that need an RSVP.**
    - Direct questions asked to Sanjay.
    - Scheduling requests.
    - Personal messages requiring acknowledgement.


    Email:
    {email_text}

    Only return the category.
    """
    return llm_call(prompt)

from email.mime.text import MIMEText
import json
from datetime import datetime as dt


def create_draft_reply(gmail_service, calendar_service, sender: str, subject: str, body: str) -> str:

    # Extract Event Time ---
    now = dt.now()
    # We provide Day Name and Time so it understands "Next Friday" or "Tonight"
    current_context = now.strftime("%A, %B %d, %Y at %H:%M") 
    
    time_prompt = f"""
    ### Role
    You are an expert Executive Assistant. Your task is to extract the **Event Start Time** from an email.

    ### Current Context (Anchor Time)
    Today is: {current_context}
    (Use this anchor to resolve relative dates like "tomorrow", "next Friday", or "in 2 days")

    ### Extraction Rules
    1. **Year Inference:** If the email mentions a date (e.g., "Jan 5") that has already passed relative to 'Today', assume it refers to the **next occurrence** (next year).
    2. **Time Inference:** - If a time is mentioned without AM/PM (e.g., "at 2"), infer the most likely time based on context (e.g., business meetings are usually 2 PM, dinner is 7 PM).
       - If no specific time is found but a date is present, default to 09:00:00 (Start of day) but mark it as approximate.
    3. **Timezones:** If a timezone is specified (EST, IST, GMT), convert it to UTC if possible, otherwise keep the local time and ignore the offset.

    ### Email Body
    "{body}"

    ### Output Format
    Return ONLY the ISO string or 'NONE'. No markdown, no quotes.
    """
    event_time = llm_call(time_prompt).strip().replace('"', '').replace("'", "")
    
    # Check Availability
    calendar_context = "No specific time mentioned in email."
    conflict_event = None
    is_free = True
    event_already_scheduled = False # Flag to prevent double-booking on 'replace'

    if event_time != "NONE" and "T" in event_time:
        print(f"\n📅 Detected Event Time: {event_time}")
        availability = check_availability(calendar_service, event_time)
        
        if availability["status"] == "BUSY":
            is_free = False
            conflict_event = availability["event"]
            calendar_context = f"WARNING: You are BUSY at this time. Conflicting Event: '{conflict_event['summary']}' (ID: {conflict_event['id']})."
        else:
            calendar_context = "You are FREE at this time."

    
    user_preferences = memory.get_all_preferences()
    current_feedback = ""

    while True:
        prompt = f"""
        You are a professional Email Assistant for Sanjay Sanapala.
        Your goal is to write a professional email reply.

        ### INPUT DATA:
        - Sender: {sender}
        - Original Subject: {subject}
        - Original Body: {body}

        ### CALENDAR CONTEXT:
        {calendar_context}

        ### LONG-TERM MEMORY (USER PREFERENCES):
        {user_preferences}
        
        ### USER FEEDBACK / ADJUSTMENTS:
        {current_feedback if current_feedback else "None (Draft the initial reply)"}

        ### GUIDELINES:
        1. **Tone:** Professional, direct, and polite.
        2. **Structure:** Greeting -> Main Point -> Call to Action -> Sign off.
        3. **Constraint:** Return strictly valid JSON.

        ### OUTPUT FORMAT (JSON ONLY):
        {{
            "To": "{sender}",
            "Subject": "Re: {subject} (or a better subject)",
            "Body": "The full email body text here..."
        }}
        """

        print("\n--- Generating Draft... ---")
        
        try:
            response_json = llm_call(prompt)
            reply_data = json.loads(response_json)
        except json.JSONDecodeError:
            print("Error: LLM did not return valid JSON. Retrying...")
            continue

        print(f"\nDRAFT PREVIEW:\nTo: {reply_data['To']}\nSubject: {reply_data['Subject']}\nBody:\n{reply_data['Body']}\n")
        
        user_choice = input("Action (yes / no / replace / [type feedback]): ").strip().lower()

        if user_choice in ["yes", "y"]:
            if event_time != "NONE" and is_free and not event_already_scheduled:
                print(f"📅 Adding event to calendar...")
                # Assuming you passed calendar_tools to this function
                add_event(calendar_service, f"Meeting with {sender}", event_time)

            # B. Send Logic
            print(f"📨 Sending email to {reply_data['To']}...")
            
            send_email(
                service=gmail_service,
                recipient=reply_data['To'], 
                subject=reply_data['Subject'], 
                body=reply_data['Body']
            )

            return "Success: Email Sent & Calendar Updated."
        # --- 2. HANDLE REPLACEMENT (REPLACE) ---
        elif "replace" in user_choice:
            # Check if there is actually a conflict to replace
            if conflict_event:
                print(f"🔄 Replacing conflicting event: '{conflict_event['summary']}'...")
                
                delete_event(calendar_service, conflict_event['id'])
                add_event(calendar_service, f"Meeting with {sender}", event_time)
                
                event_already_scheduled = True 
                is_free = True 
                conflict_event = None
                
                calendar_context = "Availability: FREE (User manually cleared the previous conflict). You MUST ACCEPT the invitation now."
                current_feedback += " I have cleared the calendar conflict. Rewrite the email to ACCEPT the invitation."
                
                print("Event swapped. Regenerating draft with acceptance...")
            
            else:
                print("⚠️ No conflicting event found to replace. (Calendar is already free or no time detected).")

        # --- 3. HANDLE CANCELLATION (NO) ---
        elif user_choice in ["no", "n"]:
            print("Operation cancelled.")
            return "Cancelled."

        # --- 4. HANDLE FEEDBACK (EVERYTHING ELSE) ---
        else:
            print("Refining draft based on feedback...")
            learning_result = learn_from_feedback(user_choice)
            if learning_result:
                print(f"{learning_result}")
                user_preferences = memory.get_all_preferences()
            current_feedback += f"\n- User requested change: {user_choice}"

@traceable(name="notify")
def process_notify(sender: str, subject: str, body: str):
    """Processes the Notification and gives a short summary or finds important events"""
    
    now = datetime.now()
    current_context = now.strftime("%A, %B %d, %Y at %H:%M")

    prompt = f"""
    ### Role
    You are an expert Executive Assistant. Your goal is to process an incoming notification email.
    
    ### Context
    Today is: {current_context}
    (Use this to resolve relative dates like "tomorrow" or "next Friday".)

    ### Input Data
    Subject: "{subject}"
    Body: "{body[:2000]}" 

    ### Tasks
    1. **Summarize**: Create a crisp, 5-10 word status update (e.g., "Amazon package arriving tomorrow").
    2. **Extract Event**: Check if this notification implies a calendar event (e.g., a flight, a webinar, a bill due date).
       - If a date is mentioned for a future event, extract it.
       - Use business logic (e.g., "Dinner" ~ 7 PM, "Meeting" ~ 9 AM-5 PM) if time is ambiguous.

    ### Output Format (Strict JSON Only)
    {{
        "summary": "The 5-10 word summary string",
        "event_found": true/false,
        "event_date": "YYYY-MM-DDTHH:MM:SS" or null,
        "reasoning": "Brief explanation of date calculation"
    }}
    """

    summary = llm_call(prompt).strip()

    try:
        # Clean potential markdown
        clean_text = summary.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        return {
            "summary": data.get("summary", "No summary available"),
            "event_found": data.get("event_found", False),
            "event_date": data.get("event_date"), # Will be None (null) if no event
            "original_subject": subject
        }
        
    except json.JSONDecodeError:
        # Fallback if LLM fails
        return {
            "summary": subject, # Fallback to subject line
            "event_found": False,
            "event_date": None,
            "original_subject": subject
        }
    

@traceable(name="draft_reply_generation")
def generate_reply_json(
    sender: str,
    subject: str,
    body: str,
    calendar_context: str,
    preferences: dict
):
    prompt = f"""
    You are a professional Email Assistant for Sanjay Sanapala.

    Sender: {sender}
    Subject: {subject}
    Body: {body}

    Calendar Context:
    {calendar_context}

    User Preferences:
    {preferences}

    Return STRICT JSON ONLY:
    {{
      "To": "{sender}",
      "Subject": "Re: {subject}",
      "Body": "Professional reply"
    }}
    """

    response = llm_call(prompt)

    if not response or not response.strip():
        raise ValueError("LLM returned empty response")

    clean = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON from LLM.\nRaw response:\n{response}"
        ) from e
