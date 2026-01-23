from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
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
