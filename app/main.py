from agent.triage import triage_email

# Sample test emails
test_emails = [
    {
        "subject": "Limited Time Offer!!!",
        "body": "Buy one get one free. Offer valid today."
    },
    {
        "subject": "Meeting tomorrow",
        "body": "Can we meet tomorrow at 10 AM to discuss the project?"
    },
    {
        "subject": "Invoice approval required",
        "body": "Please review and approve the attached invoice."
    }
]

for email in test_emails:
    decision = triage_email(email["subject"], email["body"])
    print("Subject:", email["subject"])
    print("Triage Decision:", decision)
    print("-" * 40)
