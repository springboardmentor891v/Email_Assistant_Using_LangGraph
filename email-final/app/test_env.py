from dotenv import load_dotenv
import os

load_dotenv()

print("Gemini Loaded:", bool(os.getenv("GOOGLE_API_KEY")))
print("LangSmith Loaded:", bool(os.getenv("LANGSMITH_API_KEY")))
