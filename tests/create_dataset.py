import os
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
dotenv_path = base_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

from langsmith import Client
client = Client()
dataset_name = "Email Assistant Tests"

if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Test cases for Email assistant"
    )

examples = [
    # Case A: A simple notification
    {
        "inputs": {
            "subject": "Your package has shipped",
            "body": "Your Amazon order #123 is on the way. Arriving Tuesday."
        },
        "outputs": {
            "expected_action": "NOTIFY",
            "expected_summary_contains": "Amazon order",
            "expected_event": False
        }
    },
    # Case B: A notification with a hidden event
    {
        "inputs": {
            "subject": "Webinar Registration Confirmed",
            "body": "Thanks for registering. The event is on Jan 25, 2026 at 2 PM IST."
        },
        "outputs": {
            "expected_action": "NOTIFY",
            "expected_summary_contains": "Webinar",
            "expected_event": True,
            "expected_date_snippet": "2026-01-25 14:00:00"
        }
    },
    # Case C: A direct email requiring response
    {
        "inputs": {
            "subject": "Coffee chat?",
            "body": "Hey Sanjay, are you free next week to discuss the project?"
        },
        "outputs": {
            "expected_action": "RESPOND"
        }
    }
]

client.create_examples(
    inputs=[e["inputs"] for e in examples],
    outputs=[e["outputs"] for e in examples],
    dataset_name=dataset_name
)