from langsmith import Client
from tests.cases import DRAFT_TESTS, TRIAGE_TESTS
import os
from dotenv import load_dotenv
import uuid

load_dotenv() 

if not os.environ.get("LANGCHAIN_API_KEY"):
    raise ValueError("LANGCHAIN_API_KEY is missing! Check your .env file.")

client = Client()

def upload_triage_dataset():
    dataset_name = "Email Triage Dataset"
    
    if client.has_dataset(dataset_name=dataset_name):
        print(f"Dataset '{dataset_name}' already exists.")
        return

    dataset = client.create_dataset(dataset_name=dataset_name, description="Triage classification tests")
    
    inputs = [{"email": x["email"]} for x in TRIAGE_TESTS]
    outputs = [{"expected": x["expected"]} for x in TRIAGE_TESTS]

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )
    print(f"✅ Uploaded {len(inputs)} examples to '{dataset_name}'")

def upload_draft_dataset():
    dataset_name = "Email Draft Dataset"
    
    if client.has_dataset(dataset_name=dataset_name):
        print(f"Dataset '{dataset_name}' already exists.")
        return

    dataset = client.create_dataset(dataset_name=dataset_name, description="Draft generation tests")
    
    inputs = []
    outputs = []
    
    for test in DRAFT_TESTS:
        inputs.append({
            "sender": test["sender"],
            "subject": test["subject"],
            "body": test["body"],
            "calendar_context": test["calendar_context"]
        })
        outputs.append({
            "expected_intent": test["expected_intent"]
        })

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )
    print(f"✅ Uploaded {len(inputs)} examples to '{dataset_name}'")

if __name__ == "__main__":
    upload_triage_dataset()
    upload_draft_dataset()