import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Set up LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "email-agent"

# Check for LangSmith API key
if not os.environ.get("LANGSMITH_API_KEY"):
    print("⚠️ WARNING: LANGSMITH_API_KEY not set. Agent will run but traces won't be logged to LangSmith.")
    print("To enable LangSmith logging, set the LANGSMITH_API_KEY environment variable.\n")

from agent.hitl import run_hitl_agent

if __name__ == "__main__":
    run_hitl_agent()
