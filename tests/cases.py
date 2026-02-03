DRAFT_TESTS = [
    {
        "sender": "hr@company.com",
        "subject": "Interview Reschedule",
        "body": "Hi Sanjay, can we move the interview to Friday at 2 PM instead?",
        "calendar_context": "You are BUSY from 1 PM to 3 PM.",
        "expected_intent": "decline and propose alternative time"
    },
    {
        "sender": "manager@company.com",
        "subject": "Weekly Status Update",
        "body": "Please send your weekly progress report by today evening.",
        "calendar_context": "No calendar event detected.",
        "expected_intent": "acknowledge and confirm deadline"
    },
    {
        "sender": "client@startup.io",
        "subject": "Demo Meeting",
        "body": "Are you available for a demo call tomorrow morning?",
        "calendar_context": "You are FREE between 9 AM and 12 PM.",
        "expected_intent": "accept meeting and suggest time"
    },
    {
        "sender": "finance@company.com",
        "subject": "Pending Invoice",
        "body": "Your invoice from last month is still pending. Please confirm payment status.",
        "calendar_context": "No calendar event detected.",
        "expected_intent": "acknowledge and provide status"
    },
    {
        "sender": "teammate@company.com",
        "subject": "Code Review",
        "body": "Can you review my PR by tonight?",
        "calendar_context": "You have tasks scheduled until 9 PM.",
        "expected_intent": "acknowledge and set expectation"
    },
    {
        "sender": "recruiter@external.com",
        "subject": "Offer Discussion",
        "body": "Let me know a good time to discuss the offer details this week.",
        "calendar_context": "You are FREE on Thursday afternoon.",
        "expected_intent": "propose meeting time"
    },
    {
        "sender": "support@service.com",
        "subject": "Ticket Update",
        "body": "We need additional details to proceed with your request.",
        "calendar_context": "No calendar event detected.",
        "expected_intent": "request clarification"
    },
    {
        "sender": "ceo@company.com",
        "subject": "Quick Sync",
        "body": "Can we talk for 10 minutes today?",
        "calendar_context": "You are FREE between 6 PM and 6:30 PM.",
        "expected_intent": "accept meeting with priority"
    }
]

TRIAGE_TESTS = [
    {
        "email": "Your OTP for transaction verification is 849302. Do not share it with anyone.",
        "expected": "NOTIFY"
    },
    {
        "email": "Hi Sanjay, are you free for a quick call today?",
        "expected": "RESPOND"
    },
    {
        "email": "Unsubscribe from our weekly newsletter",
        "expected": "IGNORE"
    },
    {
        "email": "Security alert: New login detected from Chrome on macOS.",
        "expected": "NOTIFY"
    },
    {
        "email": "Congratulations! You’ve won a $1000 Amazon gift card. Click here.",
        "expected": "IGNORE"
    },
    {
        "email": "Reminder: Your interview is scheduled tomorrow at 11 AM.",
        "expected": "NOTIFY"
    },
    {
        "email": "Please review the attached contract and share your feedback.",
        "expected": "RESPOND"
    },
    {
        "email": "Your monthly bank statement is ready to view.",
        "expected": "NOTIFY"
    },
    {
        "email": "Hey, just checking in to see if you saw my last email.",
        "expected": "RESPOND"
    },
    {
        "email": "This is a system-generated email. Please do not reply.",
        "expected": "IGNORE"
    }
]
