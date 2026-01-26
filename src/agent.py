import json
from src.gemini import llm_call, generate_structured_json

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

def create_draft_reply(service, sender: str, subject: str, body: str) -> str:
    current_feedback = ""
    
    while True:
        prompt = f"""
        You are a professional Email Assistant for Sanjay Sanapala.
        Your goal is to write a professional email reply.

        ### INPUT DATA:
        - Sender: {sender}
        - Original Subject: {subject}
        - Original Body: {body}
        
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
        
        user_choice = input("Action (yes / no / [type feedback]): ").strip().lower()

        if user_choice in ["yes", "y"]:
            # create_gmail_draft(service, reply_data["To"], reply_data["Subject"], reply_data["Body"])
            return "Success: Draft Created."    
        elif user_choice in ["no", "n"]:
            print("Operation cancelled.")
            return "Cancelled."
        else:
            print("Refining draft based on feedback...")
            current_feedback += f"\n- User requested change: {user_choice}"