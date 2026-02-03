import os
import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langsmith import traceable

# Using Groq for evaluation - Ultra-fast and NO quota limits!
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)


def extract_json(text: str):
    """
    Extract first JSON object from LLM output.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


@traceable(name="judge_reply")
def judge_reply(email_text: str, agent_reply: str, prediction: dict = None):
    """
    Evaluate AI email reply quality using LLM.
    
    Args:
        email_text: Original email content
        agent_reply: AI-generated reply
        prediction: Optional dict with 'output' key for LangSmith context
    
    Returns:
        dict with scores: relevance, politeness, correctness (0-10 each)
    """
    prompt = f"""
You are evaluating an AI email assistant.

Email:
{email_text}

Agent Reply:
{agent_reply}

Score the reply from 0 to 10 on:
- relevance: Does it address the email?
- politeness: Is it respectful and professional?
- correctness: Is the information accurate?

Return ONLY valid JSON with scores.
Example:
{{"relevance":8,"politeness":9,"correctness":8}}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    raw_text = response.content.strip()

    parsed = extract_json(raw_text)

    if parsed is None:
        # ✅ Graceful fallback
        return {
            "relevance": 0,
            "politeness": 0,
            "correctness": 0,
            "error": "Invalid JSON from LLM"
        }

    # Ensure all scores are within 0-10 range
    for key in ["relevance", "politeness", "correctness"]:
        if key in parsed:
            parsed[key] = min(10, max(0, parsed[key]))

    return parsed
