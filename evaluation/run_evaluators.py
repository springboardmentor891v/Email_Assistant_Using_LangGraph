import sys
import os

# 🔥 Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


from app_tools.open_ai import generate_reply
from evaluation.evaluators import judge_reply

emails = [
    "Can we meet tomorrow at 3 PM?",
    "Your OTP is 123456",
    "Please review the document I sent"
]

for email in emails:
    reply = generate_reply("Test", "test@example.com", email)
    score = judge_reply(email, reply)
    print("\nEMAIL:", email)
    print("REPLY:", reply)
    print("SCORE:", score)
