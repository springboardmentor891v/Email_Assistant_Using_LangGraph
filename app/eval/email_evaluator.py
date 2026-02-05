import os
from langsmith import tracing_context
from langsmith.evaluation import EvaluationResult
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env")

model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    google_api_key=GOOGLE_API_KEY,
    max_retries=3 # Helps handle temporary "Busy" errors
)
# Use Gemini 1.5 Flash - fast and cost-effective for evaluation


def email_reply_evaluator(run, example=None):
    # Safeguard: If the run failed, we can't evaluate content
    if run.error or not run.outputs:
        return [EvaluationResult(key="format_valid", score=0.0, comment="Run has no outputs to evaluate.")]
    
    # Extracting data from your LangGraph state
    decision = run.outputs.get("decision", {})
    reply = decision.get("reply", "N/A")
    action = decision.get("action", "N/A")

    # 1. Simple Rule-based check
    format_valid = isinstance(decision, dict) and "action" in decision

    # 2. LLM-as-a-Judge Evaluation
    prompt = f"""
    You are an Email Quality Auditor. Score the following AI response based on the chosen action.

    ACTION: {action}
    EMAIL CONTENT: \"\"\"{reply}\"\"\"

    EVALUATION CRITERIA:
    - Relevance: Does the email match the '{action}' intent?
    - Professionalism: Is the tone appropriate?

    Respond exactly in this format:
    Reasoning: <one sentence explanation>
    Score: <number between 0.0 and 1.0>
    """

    try:
        with tracing_context(enabled=False):
            raw_response = model.invoke(prompt)
            
            # --- FIX: Ensure content is treated as a string ---
            if isinstance(raw_response.content, list):
                # If content is a list of parts (common in newer models), join them
                content_text = " ".join([str(part.get('text', part)) if isinstance(part, dict) else str(part) for part in raw_response.content])
            else:
                content_text = str(raw_response.content)

            response_str = content_text.strip()
        
        # --- FIX: Robust Parsing using lower() and find() to avoid 'list' attribute errors ---
        reasoning = "Could not parse reasoning."
        score_val = 0.0

        if "Reasoning:" in response_str and "Score:" in response_str:
            reasoning = response_str.split("Reasoning:")[1].split("Score:")[0].strip()
            # Clean up the score string in case there are trailing characters
            score_part = response_str.split("Score:")[1].strip()
            # Extract only the first numeric part found
            import re
            numeric_score = re.findall(r"[-+]?\d*\.\d+|\d+", score_part)
            if numeric_score:
                score_val = float(numeric_score[0])
        
    except Exception as e:
        reasoning = f"Evaluation parsing error: {str(e)}"
        score_val = 0.0

    return [
        EvaluationResult(key="reply_quality", score=score_val, comment=reasoning),
        EvaluationResult(key="format_valid", score=1.0 if format_valid else 0.0)
    ]