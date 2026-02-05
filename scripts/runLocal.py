from app.core.gmail_client import get_gmail_service
from app.services.email_runner import run_email_assistant
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "emailAssistantEvaluation"

USER_PROMPT = """
Reply only to genuine emails.
Ignore promotions and job ads and security messages.
Schedule meetings if the email discusses a meeting, call, interview, or appointment.
"""

service, calendar_service = get_gmail_service()

run_email_assistant(
    service=service,
    calendar_service=calendar_service,
    user_prompt=USER_PROMPT,
    max_results=5
)

