import os
from concurrent.futures import ThreadPoolExecutor
from langsmith import Client, tracing_context
from app.eval.email_evaluator import email_reply_evaluator
from dotenv import load_dotenv

load_dotenv()

def evaluate_run_task(client, run):
    """Function to score one run without creating an evaluator trace."""
    with tracing_context(enabled=False):
        try:
            results = email_reply_evaluator(run)
            for result in results:
                client.create_feedback(
                    run_id=run.id,
                    key=result.key,
                    score=result.score,
                    comment=result.comment
                )
            return f"✅ Run {str(run.id)[:8]} evaluated."
        except Exception as e:
            return f"❌ Run {str(run.id)[:8]} failed: {e}"

def main():
    client = Client()
    project_name = "email-assistant-langgraph"

    # Fetch existing runs
    runs = list(client.list_runs(project_name=project_name, execution_order=1))
    
    if not runs:
        print("No runs found.")
        return

    print(f"🚀 Processing {len(runs)} runs in parallel (Tracing: OFF)...")

    # Parallel execution
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(evaluate_run_task, client, run) for run in runs]
        for i, future in enumerate(futures):
            try:
                print(f"[{i+1}/{len(runs)}] {future.result()}")
            except Exception as e:
                print(f"[{i+1}/{len(runs)}] ⚠️ Critical Error: {e}")

    print("\nEvaluation complete. Check your LangSmith dashboard columns.")

if __name__ == "__main__":
    main()