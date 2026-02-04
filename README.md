# Email Assistant Using Lang Graph

> 🤖 An intelligent, production-ready email assistant powered by Google Gemini AI, LangGraph, and Flask

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 🎯 **Intelligent Email Management**
- **AI-Powered Triage**: Automatically classifies emails into IGNORE, NOTIFY, or RESPOND
- **Smart Draft Generation**: Creates contextual responses using Gemini AI
- **Calendar Integration**: Checks availability and detects scheduling conflicts
- **Human-in-the-Loop**: Requires approval before sending emails or modifying calendar

### 🌐 **Modern Web Interface**
- **Dashboard**: Overview of unread emails, action items, and upcoming events
- **Chat Assistant**: Natural language interaction with your email system
- **Email List View**: Browse, filter, and manage emails with AI insights
- **Responsive Design**: Works seamlessly on desktop and mobile

### 🧠 **Advanced Capabilities**
- **Persistent Memory**: Learns from feedback using SQLite
- **OAuth 2.0 Security**: Secure Google authentication
- **Real-time Processing**: Live Gmail and Calendar integration
- **Extensible Architecture**: Clean MVC pattern for easy customization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Cloud Project with Gmail & Calendar APIs enabled
- Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ambient-email-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Copy .env.example to .env and fill in:
# - GEMINI_API_KEY1=your_gemini_api_key
# - FLASK_SECRET_KEY=generate_with_secrets_token_hex
```

### Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable APIs:
   - Gmail API
   - Google Calendar API
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download and save as `src/contents/credentials.json`

### Generate Flask Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add the output to your `.env` file as `FLASK_SECRET_KEY`.

### Run the Application

```bash
python app.py
```

Visit **http://localhost:5000** and login with Google!

---

## 📁 Project Structure

```
ambient-email-agent/
├── app.py                          # Flask application entry point
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
├── README.md                      # This file
├── WEB_SETUP.md                   # Detailed web setup guide
├── DEPLOYMENT_SUMMARY.md          # Feature list and architecture
│
├── src/                           # Core backend logic
│   ├── __init__.py               # Package initialization
│   ├── agent.py                  # LangGraph email agent
│   ├── auth.py                   # OAuth authentication
│   ├── gemini.py                 # Gemini AI integration
│   ├── tools.py                  # Gmail/Calendar API tools
│   ├── db.py                     # SQLite database operations
│   └── contents/                 # OAuth credentials (gitignored)
│       ├── credentials.json      # Google OAuth credentials
│       └── token.json            # OAuth token (auto-generated)
│
├── routes/                        # Flask route blueprints
│   ├── __init__.py               # Routes package
│   ├── auth_routes.py            # Authentication routes
│   ├── dashboard_routes.py       # Dashboard view
│   ├── chat_routes.py            # Chat interface
│   └── email_routes.py           # Email management
│
├── services/                      # Business logic layer
│   ├── __init__.py               # Services package
│   ├── agent_service.py          # Agent functionality wrapper
│   ├── gmail_service.py          # Gmail API operations
│   └── calendar_service.py       # Calendar API operations
│
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                 # Base template with navigation
│   ├── login.html                # OAuth login page
│   ├── dashboard.html            # Main dashboard
│   ├── chat.html                 # Chat interface
│   ├── emails.html               # Email list view
│   ├── email_detail.html         # Individual email view
│   └── triage_results.html       # Triage results display
│
├── static/                        # Static assets
│   ├── css/
│   │   └── style.css            # Custom CSS & animations
│   └── js/
│       └── main.js              # JavaScript utilities
│
├── data/                          # Application data
│   └── agent_memory.db          # SQLite database
│
└── archive/                       # Archived development files
    ├── main.py                    # Old terminal version
    ├── notebooks/                 # Jupyter notebooks
    └── docs/                      # Old documentation
```

---

## 🎯 Usage Examples

### Web Interface

#### 1. Dashboard
- View email statistics and upcoming calendar events
- See AI-generated summary of recent emails
- Quick access to triage, chat, and email list

#### 2. Chat Assistant
```
You: "Summarize my unread emails"
AI: "You have 5 unread emails. The most urgent is from..."

You: "What meetings do I have this week?"
AI: "You have 3 meetings: Project Review on Monday..."

You: "Draft a reply to the latest email from John"
AI: "I'll help you draft a reply. Here's what I suggest..."
```

#### 3. Email Triage
- Automatically categorizes emails using AI
- Shows reasoning for each classification
- Allows manual override and feedback

#### 4. Draft & Send Emails
1. Select email from list
2. Click "Draft Reply"
3. AI generates response considering calendar
4. Review and refine with feedback
5. Approve and send

### CLI Usage (Legacy)

See `archive/main.py` for terminal-based usage.

---

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Required
GEMINI_API_KEY1=your_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key_here

# Optional
FLASK_ENV=development              # Use 'production' in production
LANGCHAIN_TRACING_V2=true         # Enable LangSmith tracing
LANGCHAIN_API_KEY=your_key        # LangSmith API key
LANGCHAIN_PROJECT=EmailAssistant  # LangSmith project name
```

### Customization

- **Email Count**: Edit `routes/dashboard_routes.py`
- **Triage Logic**: Modify `src/agent.py`  
- **UI Theme**: Update `static/css/style.css`
- **Chat Behavior**: Adjust `services/agent_service.py`

---

## 🏗️ Architecture

### Clean MVC Pattern

```
┌─────────────────┐
│   Templates     │ ← Presentation (Jinja2 HTML)
└────────┬────────┘
         │
┌────────▼────────┐
│     Routes      │ ← Controller (Flask Blueprints)
└────────┬────────┘
         │
┌────────▼────────┐
│    Services     │ ← Business Logic
└────────┬────────┘
         │
┌────────▼────────┐
│  Backend (src)  │ ← Agent, Tools, DB
└─────────────────┘
```

### Key Components

- **Flask App** (`app.py`): Web server and session management
- **Routes**: HTTP request handling and response rendering
- **Services**: Business logic abstraction layer
- **Agent** (`src/agent.py`): LangGraph-based email processing
- **Tools** (`src/tools.py`): Gmail and Calendar API interactions
- **Gemini** (`src/gemini.py`): AI model integration

---

## 🔐 Security Features

- ✅ Google OAuth 2.0 Authentication
- ✅ Secure session management (24-hour lifetime)
- ✅ CSRF protection via Flask-Session
- ✅ Input sanitization and XSS prevention
- ✅ SQL injection prevention (parameterized queries)
- ✅ Credentials stored securely (not in code)

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home (redirects based on auth) |
| GET | `/auth/login` | Login page |
| GET | `/auth/authenticate` | OAuth flow |
| GET | `/auth/logout` | Logout |
| GET | `/dashboard/` | Main dashboard |
| GET | `/dashboard/run-triage` | Run email triage |
| GET | `/chat/` | Chat interface |
| POST | `/chat/send` | Send chat message (AJAX) |
| POST | `/chat/clear` | Clear chat history |
| GET | `/emails/` | Email list with filters |
| GET | `/emails/<id>` | Email details |
| POST | `/emails/<id>/draft` | Generate draft (AJAX) |
| POST | `/emails/<id>/send` | Send email (AJAX) |
| GET | `/emails/search` | Search emails |

---

## 🚀 Production Deployment

### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Waitress (Windows)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

### Environment Setup
```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your_production_secret_key
```

### Production Checklist
- [ ] Use HTTPS (Nginx reverse proxy + Let's Encrypt)
- [ ] Strong `FLASK_SECRET_KEY`
- [ ] Production WSGI server (Gunicorn/Waitress)
- [ ] Enable logging and monitoring
- [ ] Set up rate limiting
- [ ] Configure CORS if needed
- [ ] Regular database backups

---

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Change port in app.py or run with different port
python app.py --port 8000
```

**OAuth Errors**
- Ensure `src/contents/credentials.json` exists
- Check Gmail & Calendar APIs are enabled
- Verify redirect URI in Google Cloud Console

**Import Errors**
```bash
# Ensure you're in the project root
cd ambient-email-agent
python app.py
```

**Session Issues**
```bash
# Clear Flask session cache
rm -rf flask_session/  # Linux/Mac
Remove-Item flask_session -Recurse  # Windows
```

See `WEB_SETUP.md` for detailed troubleshooting.

---

## 📚 Documentation

- **[WEB_SETUP.md](WEB_SETUP.md)** - Detailed web interface setup
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Architecture and features
- **[LICENSE](LICENSE)** - MIT License

---

## 🤝 Contributing

This is a portfolio/educational project. Feel free to fork and customize!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎓 Learning Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Google Gemini AI](https://ai.google.dev/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gmail API Guide](https://developers.google.com/gmail/api)
- [Google Calendar API](https://developers.google.com/calendar)

---

## 💡 Future Enhancements

- [ ] Full-text email search
- [ ] Interactive calendar view
- [ ] User settings page
- [ ] Email attachments support
- [ ] Real-time notifications (WebSockets)
- [ ] Analytics dashboard
- [ ] Export functionality
- [ ] Mobile companion app
- [ ] Multi-account support
- [ ] Dark mode theme

---

## 🙏 Acknowledgments

- Google Gemini AI for intelligent email processing
- LangGraph for agent workflow orchestration
- Flask for the web framework
- Tailwind CSS for beautiful UI
- Gmail & Calendar APIs for email/calendar integration

---

## 📞 Support

For issues and questions:
1. Check `WEB_SETUP.md` for detailed setup instructions
2. Review `DEPLOYMENT_SUMMARY.md` for architecture details
3. Open an issue on GitHub
4. Check the troubleshooting section above

---

**Built with ❤️ using Flask, Google Gemini AI, and LangGraph**

**Perfect for portfolios, interviews, and learning modern AI application development!**
