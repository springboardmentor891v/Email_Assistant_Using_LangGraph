# main.py
from dotenv import load_dotenv
load_dotenv()
from agent.hitl import run_hitl_agent


if __name__ == "__main__":
    run_hitl_agent()
