from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

triage_prompt = PromptTemplate(
    input_variables=["subject", "body"],
    template="""
You are an intelligent email assistant.

Classify the following email into ONLY ONE category:

1. ignore – spam, ads, newsletters, promotions
2. notify_human – important but needs human decision
3. respond_act – safe for the AI to respond or act

Email Subject:
{subject}

Email Body:
{body}

Respond with ONLY ONE WORD:
ignore OR notify_human OR respond_act
"""
)

def triage_email(subject: str, body: str) -> str:
    chain = triage_prompt | llm
    response = chain.invoke({
        "subject": subject,
        "body": body
    })
    return response.content.strip().lower()

def triage_node(state: dict) -> dict:
    """
    LangGraph-compatible wrapper for triage_email
    Handles both raw input and propagated state safely.
    """

    # Be defensive about input keys
    subject = state.get("email_subject") or state.get("subject")
    body = state.get("email_body") or state.get("body")

    if subject is None or body is None:
        raise KeyError(
            f"triage_node missing required keys. "
            f"Got keys: {list(state.keys())}"
        )

    decision = triage_email(
        subject=subject,
        body=body
    )

    return {
        **state,
        "email_subject": subject,   # normalize for downstream nodes
        "email_body": body,
        "triage_decision": decision,
        "intent": decision
    }


