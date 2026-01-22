emails = [
    {
        "sender": "hr@company.com",
        "subject": "Interview Confirmation",
        "body": "Hi Sana,\n\nYour interview has been scheduled for Monday at 10 AM.\n\nRegards,\nHR Team"
    },
    {
        "sender": "project.manager@office.com",
        "subject": "Project Update Required",
        "body": "Hello Sana,\n\nPlease share the latest project status by EOD.\n\nThanks,\nProject Manager"
    },
    {
        "sender": "friend@gmail.com",
        "subject": "Weekend Plan",
        "body": "Hi Sana,\n\nAre we meeting this weekend?\n\nCheers!"
    }
]
def read_email(email):
    sender = email["sender"]
    subject = email["subject"]
    body = email["body"]

    print("👤 From:", sender)
    print("📧 Subject:", subject)
    print("📝 Body:")
    print(body)
    print("-" * 50)
    for email in emails:
    read_email(email)
    for email in emails:
    read_email(email)