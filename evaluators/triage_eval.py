from src.agent import traige_email
from tests.cases import TRIAGE_TESTS
from evaluators.groq_judge import groq_judge

def evaluate_triage():
    total = len(TRIAGE_TESTS)
    passed = 0
    results = []

    print("\n📩 Email Triage Evaluation")
    print("-" * 40)

    for idx, test in enumerate(TRIAGE_TESTS, start=1):
        prediction = traige_email(test["email"])

        judge_prompt = f"""
        Email:
        {test['email']}

        Expected Category: {test['expected']}
        Model Output: {prediction}

        Decide STRICTLY if the model output matches the expected category.

        Return JSON ONLY:
        {{
          "score": 0 or 1,
          "reason": "short explanation"
        }}
        """

        verdict = groq_judge(judge_prompt)

        is_pass = verdict.get("score", 0) == 1
        status = "✅ PASS" if is_pass else "❌ FAIL"

        if is_pass:
            passed += 1

        print(f"\nTest {idx}: {status}")
        print(f"Email     : {test['email'][:80]}{'...' if len(test['email']) > 80 else ''}")
        print(f"Expected  : {test['expected']}")
        print(f"Predicted : {prediction}")
        print(f"Reason    : {verdict.get('reason', 'No reason provided')}")

        results.append({
            "email": test["email"],
            "expected": test["expected"],
            "predicted": prediction,
            "status": status,
            "reason": verdict.get("reason", "")
        })

    accuracy = round((passed / total) * 100, 2)

    print("\n" + "=" * 40)
    print(f"📊 Triage Accuracy: {accuracy}% ({passed}/{total})")
    print("=" * 40)

    return {
        "accuracy": accuracy,
        "passed": passed,
        "total": total,
        "results": results
    }
