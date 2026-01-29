📧 Email-Final: AI-Powered Email Assistant with Human-in-the-Loop

An intelligent email assistant that reads real Gmail emails, drafts formal AI-generated replies, allows human approval/editing, and sends replies in the same email thread — built using LangGraph, Gemini, and Gmail API.

🚀 Features

📥 Reads real emails from Gmail inbox

✍️ Drafts formal, professional replies using Gemini AI

👤 Human-in-the-Loop (Approve / Edit / Reject)

📧 Sends replies in the same Gmail thread

🧠 Fallback logic when AI quota is exhausted

🗂 Persistent memory using SQLite

📊 Politeness evaluation node (extensible)

📅 Optional Google Calendar event creation

🧩 Modular LangGraph workflow

🔒 Safe, production-grade error handling

🏗️ Architecture Overview
Gmail Inbox
     ↓
Inbox Reader
     ↓
Draft Reply (AI / Fallback)
     ↓
Human Approval
     ↓
Politeness Evaluation
     ↓
Send Reply (Same Thread)
     ↓
Optional Calendar Event


All data flows through a shared EmailState using LangGraph.

📁 Project Structure
email-final/
├── app/
│   ├── inbox.py           # Fetch Gmail emails
│   ├── draft.py           # AI reply generation (formal)
│   ├── eval.py            # Politeness evaluation
│   ├── send.py            # Send reply via Gmail
│   ├── gmail.py           # Gmail API utilities
│   ├── calendar.py        # Google Calendar integration
│   ├── calendar_node.py   # Calendar workflow node
│   ├── graph.py           # LangGraph pipeline
│   ├── state.py           # Shared EmailState
│   ├── db.py              # SQLite persistence
│   └── test_draft.py      # End-to-end test runner
│
├── data/
│   └── email_final.db     # SQLite database
│
├── .env                   # API keys & config
├── requirements.txt
└── README.md

⚙️ Setup Instructions
1️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Configure Environment Variables

Create .env file:

GOOGLE_API_KEY=your_gemini_api_key
GMAIL_CLIENT_SECRET=credentials.json

4️⃣ Enable Google APIs

Enable the following in Google Cloud Console:

Gmail API

Google Calendar API (optional)

Add your Gmail ID as a test user.

5️⃣ Initialize Database
python app/db.py

6️⃣ Run the Project
python -m app.test_draft

👤 Human-in-the-Loop Flow

When an email is detected:

Choose an action:
1️⃣ Approve
2️⃣ Edit
3️⃣ Reject


Approve → reply is sent

Edit → you modify reply before sending

Reject → nothing is sent

🧠 AI Drafting Logic

Uses Gemini Flash

Always formal & professional

If quota is exceeded → safe fallback reply

No crashes, production-safe

🛡️ Error Handling

Gemini quota exhaustion → fallback reply

Missing subject → handled gracefully

Missing thread ID → safe send

All state safely preserved

🧪 Testing

End-to-end test:

python -m app.test_draft


This simulates:

Inbox read

Draft generation

Human approval

Gmail send

Calendar trigger (optional)

📌 Technologies Used

Python 3.11

LangGraph

Google Gemini API

Gmail API

Google Calendar API

SQLite

OAuth 2.0

🎯 Use Cases

Smart email reply assistant

HR / Interview automation

Leave request handling

Professional inbox management

AI agent systems with human control

✅ Project Status

✔ Completed
All core features implemented and tested successfully.