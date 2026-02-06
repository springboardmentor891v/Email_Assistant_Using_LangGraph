from langsmith.evaluation import evaluate
from langsmith.schemas import Run, Example
from src.agent import generate_reply_json, traige_email
from evaluators.groq_judge import groq_judge
import json

def triage_target(inputs: dict) -> dict:
    """Wraps the triage agent to accept a dict and return a dict."""
    result = traige_email(inputs["email"])
    return {"category": result}

def draft_target(inputs: dict) -> dict:
    """Wraps the draft agent."""
    reply = generate_reply_json(
        sender=inputs["sender"],
        subject=inputs["subject"],
        body=inputs["body"],
        calendar_context=inputs["calendar_context"],
        preferences={}
    )
    return {"draft": str(reply)}

def triage_evaluator(run: Run, example: Example) -> dict:
    """
    Custom evaluator using your specific Groq Judge prompt for Triage.
    """
    model_output = run.outputs["category"]
    expected = example.outputs["expected"]
    email_text = example.inputs["email"]

    judge_prompt = f"""
    Email:
    {email_text}

    Expected Category: {expected}
    Model Output: {model_output}

    Decide STRICTLY if the model output matches the expected category.
    
    Return JSON ONLY:
    {{
        "score": 0 or 1,
        "reason": "short explanation"
    }}
    """
    
    try:
        verdict = groq_judge(judge_prompt)
        return {
            "key": "triage_accuracy",
            "score": verdict.get("score", 0),
            "comment": verdict.get("reason", "No reason provided")
        }
    except Exception as e:
        return {"key": "triage_accuracy", "score": 0, "comment": str(e)}

def draft_evaluator(run: Run, example: Example) -> dict:
    """
    Custom evaluator using your specific Groq Judge prompt for Drafts.
    """
    draft_reply = run.outputs["draft"]
    expected_intent = example.outputs["expected_intent"]
    inputs = example.inputs

    judge_prompt = f"""
    Email Context:
    Subject: {inputs['subject']}
    Body: {inputs['body']}

    Draft Reply:
    {draft_reply}

    Expected Intent:
    {expected_intent}

    Evaluate STRICTLY:
    - Reply is professional
    - Expected intent is satisfied
    - Output is valid JSON

    Return JSON ONLY:
    {{
        "score": 0 or 1,
        "reason": "brief explanation"
    }}
    """

    try:
        verdict = groq_judge(judge_prompt)
        return {
            "key": "draft_quality",
            "score": verdict.get("score", 0),
            "comment": verdict.get("reason", "No reason provided")
        }
    except Exception as e:
        return {"key": "draft_quality", "score": 0, "comment": str(e)}


def run_all_evals():
    print("🚀 Starting Triage Evaluation...")
    evaluate(
        triage_target,
        data="Email Triage Dataset",
        evaluators=[triage_evaluator],
        experiment_prefix="triage-groq-test",
        metadata={"version": "1.0", "model": "llama-3-70b"}
    )

    print("\n🚀 Starting Draft Evaluation...")
    evaluate(
        draft_target,
        data="Email Draft Dataset",
        evaluators=[draft_evaluator],
        experiment_prefix="draft-groq-test",
        metadata={"version": "1.0", "model": "llama-3-70b"}
    )

if __name__ == "__main__":
    run_all_evals()