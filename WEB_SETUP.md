# Web Interface Setup Guide

## 🌐 Flask Web Application

The Email Assistant now includes a production-ready web interface built with Flask.

## 📁 New Project Structure

```
ambient-email-agent/
├── app.py                       # Flask application entry point
├── routes/                      # Route blueprints
│   ├── __init__.py
│   ├── auth_routes.py          # OAuth authentication
│   ├── dashboard_routes.py     # Main dashboard
│   ├── chat_routes.py          # Chatbot interface
│   └── email_routes.py         # Email list and actions
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── agent_service.py        # Agent functionality wrapper
│   ├── gmail_service.py        # Gmail API wrapper
│   └── calendar_service.py     # Calendar API wrapper
├── templates/                   # Jinja2 HTML templates
│   ├── base.html              # Base template with nav
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard
│   ├── chat.html              # Chat interface
│   ├── emails.html            # Email list
│   └── triage_results.html    # Triage results
├── static/                      # Static assets
│   ├── css/
│   │   └── style.css          # Custom CSS
│   └── js/
│       └── main.js            # JavaScript utilities
├── src/                         # Existing backend (unchanged)
└── data/                        # SQLite database
```

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Update your `.env` file to include Flask configuration:

```bash
# Existing variables
GEMINI_API_KEY1=your_gemini_api_key_here

# New Flask variables
FLASK_SECRET_KEY=your_random_secret_key_here
FLASK_ENV=development  # Use 'production' in production
```

Generate a secure secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### 3. Run the Web Application

```bash
python app.py
```

The app will be available at: **http://localhost:5000**

## 🎯 Features

### 1. **Dashboard** (`/dashboard`)
- Welcome message with user info
- Summary cards:
  - Unread emails count
  - Emails requiring response
  - Upcoming calendar events
- AI-generated email summary
- Quick action buttons
- Recent emails and events preview

### 2. **Chat Interface** (`/chat`)
- ChatGPT-style conversation UI
- Natural language commands:
  - "Summarize my unread emails"
  - "What meetings do I have this week?"
  - "How many unread emails do I have?"
- Real-time responses with typing indicator
- Quick action buttons for common tasks
- Chat history persistence

### 3. **Email List** (`/emails`)
- Table view of all emails
- AI triage categories (IGNORE/NOTIFY/RESPOND)
- Filter by: All, Unread, Starred
- Actions per email:
  - View details
  - Generate draft reply
  - Send with approval

### 4. **Human-in-the-Loop Approval**
- Draft reply modal shows:
  - To, Subject, Body
  - Calendar conflict warnings
  - Feedback input for refinement
- Actions:
  - ✅ **Send** - Approve and send email
  - 🔄 **Refine** - Provide feedback to improve draft
  - ❌ **Cancel** - Discard draft

### 5. **Triage Results** (`/dashboard/run-triage`)
- Automated email classification
- Summary statistics
- Reasoning for each classification
- Category-based visual indicators

## 🔐 Authentication Flow

1. User visits `/` (redirects to `/auth/login`)
2. Clicks "Sign in with Google"
3. OAuth flow authenticates with Google
4. User grants Gmail + Calendar permissions
5. Redirected to `/dashboard`
6. Session stored for 24 hours

### Logout
- Visit `/auth/logout` or click Logout button
- Clears session and returns to login page

## 🎨 UI/UX Design

- **Framework**: Tailwind CSS (via CDN)
- **Icons**: Font Awesome 6
- **Fonts**: Inter (Google Fonts)
- **Color Scheme**: Purple/Blue gradient theme
- **Animations**: Smooth transitions and hover effects

### Design Principles
- Clean, modern interface
- Mobile-responsive
- Accessibility-focused
- Card-based layout
- Gradient accents

## 📱 API Endpoints

### Authentication
- `GET /auth/login` - Login page
- `GET /auth/authenticate` - Initiate OAuth
- `GET /auth/logout` - Logout user

### Dashboard
- `GET /dashboard/` - Main dashboard
- `GET /dashboard/run-triage` - Run email triage

### Chat
- `GET /chat/` - Chat interface
- `POST /chat/send` - Send message (AJAX)
- `POST /chat/clear` - Clear chat history

### Emails
- `GET /emails/` - Email list
- `GET /emails/<id>` - Email details
- `POST /emails/<id>/draft` - Generate draft (AJAX)
- `POST /emails/<id>/send` - Send approved draft (AJAX)
- `GET /emails/search?q=query` - Search emails

## 🔧 Configuration

### Number of Emails Displayed
Edit `routes/dashboard_routes.py`:
```python
recent_emails = GmailService.get_recent_emails(gmail_service, max_results=5)
```

### Chat History Length
Edit `routes/chat_routes.py`:
```python
session['chat_history'] = session['chat_history'][-20:]  # Keep last 20
```

### Session Timeout
Edit `app.py`:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python app.py --port 8000
```

Or modify `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Template Not Found
Ensure `templates/` directory exists and contains all `.html` files.

### Static Files Not Loading
Check that `static/css/style.css` and `static/js/main.js` exist.

### OAuth Errors
1. Ensure `src/contents/credentials.json` exists
2. Check Google Cloud Console:
   - Gmail API enabled
   - Calendar API enabled
   - OAuth consent screen configured
   - Redirect URI includes http://localhost:5000

### Session Issues
```bash
# Clear Flask session cache
rm -rf flask_session/  # Linux/Mac
Remove-Item flask_session -Recurse  # Windows
```

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

### Environment Variables
```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your_production_secret_key
```

### HTTPS Setup
Use a reverse proxy like Nginx with Let's Encrypt SSL certificate.

### Database
The app uses the existing SQLite database in `data/agent_memory.db`.

## 📊 Architecture

### Service Layer Pattern
- **Routes** handle HTTP requests/responses
- **Services** contain business logic and integrate with backend
- **Templates** render HTML with Jinja2
- **Static files** provide CSS/JS assets

### Integration with Existing Backend
All routes use the existing `src/` modules:
- `src/auth.py` - OAuth authentication
- `src/agent.py` - Email triage and drafting
- `src/tools.py` - Gmail and Calendar APIs
- `src/gemini.py` - Gemini AI calls
- `src/db.py` - Memory storage

## 🎓 Code Quality

- Clean MVC separation
- Well-commented code
- Production-ready error handling
- Security best practices:
  - CSRF protection (via Flask-Session)
  - Input sanitization
  - SQL injection prevention
  - XSS protection
  - Secure session management

## 📚 Next Steps

1. **Add Email Search**: Implement search functionality in email list
2. **Calendar View**: Create calendar interface for event management
3. **Settings Page**: User preferences and configuration
4. **Export Data**: Export emails and conversations
5. **Analytics**: Usage statistics and insights
6. **Mobile App**: React Native or Flutter companion app

## 🤝 Contributing

The web interface is designed to be easily extensible:
- Add new routes in `routes/`
- Add new services in `services/`
- Add new templates in `templates/`
- Customize styles in `static/css/style.css`

---

**Built with** ❤️ **using Flask, Tailwind CSS, and Google Gemini AI**
