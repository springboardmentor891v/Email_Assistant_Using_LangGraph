from .state import EmailState
from .config import DEV_MODE

# 🔒 DEV MODE: bypass Gemini to avoid quota errors
DEV_MODE = True   # ⬅️ SET False when quota is available

def triage_email(state: EmailState) -> EmailState:
    if DEV_MODE:
        # Always respond during development
        state["action"] = "respond"
        return state

    # ---- REAL LLM LOGIC (kept for later) ----
    from dotenv import load_dotenv
    load_dotenv()

    from google import genai
    import os

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    MODEL = "models/gemini-flash-latest"

    prompt = f"""
Decide what to do with the email below.
Reply with one word only: ignore, notify_human, or respond.

Subject: {state['subject']}
Body: {state['body']}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    decision = response.text.strip().lower()
    state["action"] = decision if decision in ["ignore", "notify_human", "respond"] else "respond"
    state["reply"] = reply
    return state
