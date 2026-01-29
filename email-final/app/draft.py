from .state import EmailState
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

def draft_reply(state: EmailState) -> EmailState:
    """
    Draft a FORMAL reply using Gemini.
    If Gemini quota is exceeded, fall back to a formal template.
    """

    try:
        client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        MODEL = "models/gemini-flash-latest"

        prompt = f"""
You are a professional corporate email assistant.

Write a FORMAL, POLITE, and CLEAR reply.
Use professional language only.
No casual words. No emojis.

Email details:
Subject: {state["subject"]}
Email body:
{state["body"]}

Return ONLY the email reply content.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        state["reply"] = response.text.strip()
        return state

    except Exception as e:
        # 🔒 FALLBACK (quota-safe, always works)
        state["reply"] = f"""
Subject: Re: {state['subject']}

Dear Sir/Madam,

Thank you for your email.

I acknowledge receipt of your message and will respond with further details as required.

Kind regards,  
Sindhuja
""".strip()

        return state
