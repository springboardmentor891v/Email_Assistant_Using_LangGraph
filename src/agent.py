import json
from src.gemini import llm_call, generate_structured_json
from src.tools import add_event, delete_event, send_email, check_availability
from src.db import MemoryManager

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
    current_date_str = now.strftime("%A, %B %d, %Y") # e.g., "Monday, January 26, 2026"
    current_year = now.year

    time_prompt = f"""
    Context: Today is {current_date_str}.
    
    Task: Extract the event start time from the email below.
    - If a date (like "28 Jan") is mentioned without a year, assume the year is {current_year}.
    - Convert the time to ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
    - If NO specific time is found, return exactly 'NONE'.
    
    Email Body:
    "{body}"
    
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