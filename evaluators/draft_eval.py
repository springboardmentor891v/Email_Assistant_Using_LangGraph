from src.agent import generate_reply_json
from tests.cases import DRAFT_TESTS
from evaluators.groq_judge import groq_judge

def evaluate_drafts():
    total = len(DRAFT_TESTS)
    passed = 0
    results = []

    print("\n🧪 Draft Reply Evaluation")
    print("-" * 40)

    for idx, test in enumerate(DRAFT_TESTS, start=1):
        try:
            reply = generate_reply_json(
                test["sender"],
                test["subject"],
                test["body"],
                test["calendar_context"],
                preferences={}
            )

            judge_prompt = f"""
            Email Context:
            Subject: {test['subject']}
            Body: {test['body']}

            Draft Reply:
            {reply}

            Expected Intent:
            {test['expected_intent']}

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

            verdict = groq_judge(judge_prompt)
            is_pass = verdict.get("score", 0) == 1

        except Exception as e:
            verdict = {
                "score": 0,
                "reason": f"Draft generation failed: {str(e)}"
            }
            is_pass = False

        status = "✅ PASS" if is_pass else "❌ FAIL"
        if is_pass:
            passed += 1

        print(f"\nTest {idx}: {status}")
        print(f"Subject : {test['subject']}")
        print(f"Reason  : {verdict['reason']}")

        results.append({
            "subject": test["subject"],
            "status": status,
            "reason": verdict["reason"]
        })

    accuracy = round((passed / total) * 100, 2)

    print("\n" + "=" * 40)
    print(f"📊 Draft Evaluation Accuracy: {accuracy}% ({passed}/{total})")
    print("=" * 40)

    return {
        "accuracy": accuracy,
        "passed": passed,
        "total": total,
        "results": results
    }
