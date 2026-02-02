# Email Assistant Using LangGraph

An intelligent, autonomous email assistant powered by Google's Gemini AI and LangGraph. This agent proactively manages your email workflows with persistent memory, calendar integration, and human-in-the-loop controls.

## 📋 Project Objectives

This project creates a sophisticated "ambient" agent that moves beyond simple reactive responses:

1. **Proactive Triage**: Automatically classify emails into:
   - **IGNORE**: Spam, advertisements, marketing emails
   - **NOTIFY**: Important informational emails (OTPs, events, updates)
   - **RESPOND**: Emails requiring responses (drafts created with human approval)

2. **Persistent Memory**: Learn and adapt over time using feedback and preferences stored in SQLite

3. **Human-in-the-Loop**: Autonomous for low-risk tasks, requires approval for critical operations

4. **Calendar Integration**: Automatically check availability, detect conflicts, and schedule events

5. **Real-world Deployment**: Connected to live Gmail service with OAuth authentication

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Cloud Project with Gmail API and Google Calendar API enabled
- Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Installation

1. **Clone and install dependencies:**
```bash
git clone <your-repo-url>
cd ambient-email-agent
pip install -r requirements.txt
```

2. **Set up environment variables:**

Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY1=your_gemini_api_key_here
```

3. **Configure Google Cloud credentials:**

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create or select a project
   
   c. Enable APIs:
      - Gmail API
      - Google Calendar API
   
   d. Create OAuth 2.0 credentials:
      - Navigate to "APIs & Services" → "Credentials"
      - Click "Create Credentials" → "OAuth client ID"
      - Select "Desktop app"
      - Download the JSON file
   
   e. Save as `src/contents/credentials.json`

4. **Run the application:**
```bash
python main.py
```

On first run, authenticate with Google in your browser. The token will be saved for future use.

## 📁 Project Structure

```
ambient-email-agent/
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── main.py                       # Main entry point
├── LICENSE                       # License file
├── README.md                     # This file
├── QUICKSTART.md                 # Quick setup guide
│
├── data/
│   └── agent_memory.db          # SQLite database for persistent memory
│
├── src/
│   ├── contents/
│   │   ├── credentials.json     # Google OAuth credentials (you add this)
│   │   └── token.json          # Auto-generated after first auth
│   ├── auth.py                  # Google authentication logic
│   ├── agent.py                 # Email triage and response generation
│   ├── gemini.py               # Gemini AI integration
│   ├── tools.py                # Gmail and Calendar API tools
│   └── db.py                   # Memory management with SQLite
│
└── notebooks/
    └── Email_Assistant.ipynb    # Jupyter notebook for testing
```

## 🎯 How It Works

### Email Processing Flow

1. **Fetch**: Retrieves recent emails from Gmail
2. **Triage**: AI classifies each email (IGNORE/NOTIFY/RESPOND)
3. **Analyze**: For RESPOND emails:
   - Extracts event times and details
   - Checks calendar availability
   - Detects scheduling conflicts
4. **Draft**: Generates contextual response using Gemini AI
5. **Review**: Human approval loop with feedback
6. **Execute**: Sends email and updates calendar
7. **Learn**: Stores feedback for future improvement

### Interactive Commands

When reviewing a draft email:
- `yes` or `y` → Approve and send
- `no` or `n` → Cancel operation
- `replace` → Replace conflicting calendar event
- Any text → Provide feedback to refine the draft

## 🔧 Configuration

### Adjust Number of Emails Processed

Edit `main.py`:
```python
messages = fetch_recent_emails(gmail_service, 1)  # Change 1 to desired number
```

### Customize Triage Categories

Edit `src/agent.py` in the `traige_email()` function to modify classification rules.

### Change AI Model

Edit `src/gemini.py`:
```python
model="gemini-2.5-flash-lite"  # Options: gemini-pro, gemini-2.0-flash, etc.
```

### Modify Calendar Event Duration

Edit `src/tools.py` in the calendar functions to change default event length (currently 1 hour).

## 📓 Using Jupyter Notebooks

For testing and experimentation, use the included notebook:

```bash
jupyter notebook notebooks/Email_Assistant.ipynb
```

**Note:** The notebook runs from the `notebooks/` directory, so it uses relative paths like `../src/contents/credentials.json`.

## 📝 Features

✅ Automatic email triage and classification  
✅ Context-aware response generation with Gemini AI  
✅ Google Calendar integration and conflict detection  
✅ Learning from user feedback and preferences  
✅ Human-in-the-loop approval system  
✅ Persistent memory with SQLite database  
✅ Event scheduling and rescheduling support  
✅ OAuth 2.0 authentication with token refresh  

## 🐛 Troubleshooting

### Authentication Issues

**Error: `credentials.json not found`**
```bash
# Ensure file is in correct location:
src/contents/credentials.json
```

**Error: Invalid token or expired credentials**
```bash
# Delete token and re-authenticate:
rm src/contents/token.json
python main.py
```

### API Issues

**Error: `GEMINI_API_KEY1 not set`**
- Check `.env` file exists in root directory
- Verify variable name is `GEMINI_API_KEY1`
- Ensure no extra spaces or quotes

**Error: API quota exceeded**
- Gmail/Calendar APIs have daily quotas
- Wait 24 hours or request quota increase in Google Cloud Console

### Import/Module Errors

```bash
pip install -r requirements.txt --upgrade
```

### Empty token.json Error

If `token.json` exists but is empty:
```bash
# Delete and re-authenticate
rm src/contents/token.json
python main.py
```

## 🔒 Security Best Practices

- ✅ Never commit `.env` or `credentials.json` to version control
- ✅ Keep `token.json` private and secure
- ✅ Use environment variables for all API keys
- ✅ Regularly rotate credentials and tokens
- ✅ Review OAuth scopes and permissions

## 📚 Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google Cloud Console](https://console.cloud.google.com/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

See LICENSE file for details.

---

**Built with** ❤️ **using Google Gemini AI, LangGraph, and Gmail API**

