import sys
import os

# 🔥 Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Set up LangSmith tracing for evaluation
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "email-agent-evaluation"

if not os.environ.get("LANGSMITH_API_KEY"):
    print("⚠️ WARNING: LANGSMITH_API_KEY not set. Evaluation will run but won't be logged to LangSmith.")

from app_tools.open_ai import generate_reply_unified
from evaluation.evaluators import judge_reply
import json

# Load test data
with open(os.path.join(os.path.dirname(__file__), "test_data.json")) as f:
    test_emails = json.load(f)

print("=" * 60)
print("🚀 Running Email Assistant Evaluation with LangSmith")
print("=" * 60)

results = []

for i, test_case in enumerate(test_emails, 1):
    email = test_case["email"]
    expected_action = test_case.get("expected_action", "respond")
    
    print(f"\n📧 Test Case {i}: {expected_action.upper()}")
    print(f"Email: {email[:80]}...")
    
    # Generate reply
    reply = generate_reply_unified(
        subject="Test Subject",
        sender="test@example.com",
        body=email
    )
    
    print(f"Reply: {reply[:100]}...")
    
    # Evaluate reply
    score = judge_reply(email, reply)
    
    result = {
        "test_case": i,
        "email": email,
        "expected_action": expected_action,
        "reply": reply,
        "scores": score
    }
    results.append(result)
    
    print(f"✅ Scores: {score}")

# Summary
print("\n" + "=" * 60)
print("📊 EVALUATION SUMMARY")
print("=" * 60)

avg_relevance = sum(r["scores"].get("relevance", 0) for r in results) / len(results)
avg_politeness = sum(r["scores"].get("politeness", 0) for r in results) / len(results)
avg_correctness = sum(r["scores"].get("correctness", 0) for r in results) / len(results)

print(f"Average Relevance: {avg_relevance:.2f}/10")
print(f"Average Politeness: {avg_politeness:.2f}/10")
print(f"Average Correctness: {avg_correctness:.2f}/10")

overall = (avg_relevance + avg_politeness + avg_correctness) / 3
print(f"\n🎯 Overall Score: {overall:.2f}/10")

if os.environ.get("LANGSMITH_API_KEY"):
    print("\n✅ Results logged to LangSmith!")

