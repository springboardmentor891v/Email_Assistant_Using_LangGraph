import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "email-agent"
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGSMITH_API_KEY", "")

from agent.hitl import run_hitl_agent

if __name__ == "__main__":
    run_hitl_agent()
