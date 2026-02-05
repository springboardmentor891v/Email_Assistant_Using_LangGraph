from langchain_google_genai import ChatGoogleGenerativeAI
from config import OPENAI_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemma-3-27b-it",
    google_api_key=OPENAI_API_KEY,
    temperature=0.3
)
