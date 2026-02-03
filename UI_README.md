# Email Assistant Pro - Streamlit UI

A comprehensive web-based interface for managing and responding to emails with AI-powered assistance.

## Features

### 📬 Inbox Management
- **Real-time Gmail Integration**: Connect directly to your Gmail account
- **Smart Email Categorization**: Automatically categorizes emails as:
  - 🔴 **Important**: Critical emails, meetings, urgent matters
  - 🟡 **Promotional**: Sales, discounts, offers
  - 🔵 **Social**: Social media notifications
  - 🟢 **Other**: General emails

- **Email Statistics Dashboard**:
  - Total unread emails count
  - Category distribution
  - Visual charts and metrics

### ✍️ AI-Powered Reply Management
- **Smart Reply Generation**: AI generates contextual email replies
- **Quality Evaluation**: Scores replies on:
  - ✨ Relevance (0-10)
  - 😊 Politeness (0-10)
  - ✅ Correctness (0-10)

- **Calendar Integration**:
  - Automatic event detection from emails
  - Calendar conflict detection
  - Alternative meeting time suggestions
  - One-click calendar event creation

- **Learning from Feedback**: System learns your preferences with each interaction

### 📊 Analytics Dashboard
- Email category distribution charts
- Response quality metrics
- Historical statistics
- Trend analysis

### ⚙️ User Preferences
- Configurable reply tone (professional, friendly, formal, casual)
- Reply length preference (short, medium, long)
- Automatic preferences learning

## Installation

```bash
pip install streamlit
```

## Running the App

```bash
streamlit run ui/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### 1. Initial Setup
1. Click **"Connect to Gmail"** to authenticate with your Gmail account
2. Grant necessary permissions for Gmail and Calendar access

### 2. Load Emails
1. Click **"Refresh Emails"** to load your unread emails
2. Emails are automatically categorized

### 3. Review & Respond
1. Select an email from the inbox
2. View full email content
3. AI automatically generates a reply
4. Review quality scores (Relevance, Politeness, Correctness)
5. Edit if needed or send directly

### 4. Handle Calendar Invites
- If email contains a meeting/event:
  - System automatically detects it
  - Checks for calendar conflicts
  - Suggests alternative times if conflict
  - Creates event with one click

### 5. Manual Reply Mode
- Use "Reply Manager" tab to compose custom replies
- AI can polish and enhance your message
- Send directly from the interface

## Tab Overview

### 📬 Inbox Tab
- View all emails with smart categorization
- Quick email stats in sidebar
- Click email to view details and reply
- Mark emails as read
- Filter by category

### ✍️ Reply Manager Tab
- Compose custom email replies
- AI enhancement/polishing
- Direct sending capability

### 📊 Analytics Tab
- Detailed email statistics
- Category distribution charts
- Average reply quality metrics
- Historical performance data

## Keyboard Shortcuts
- **R**: Refresh emails
- **C**: Connect to Gmail
- **A**: Generate reply automatically

## Architecture Integration

The Streamlit UI integrates with:
- **Gmail API**: For email reading and sending
- **Google Calendar API**: For event management
- **LangGraph/Gemini AI**: For intelligent reply generation
- **LangSmith**: For evaluation and logging
- **SQLite**: For preference memory storage

## Troubleshooting

### "Connection error: ..."
- Ensure you have valid Gmail credentials
- Check internet connection
- Verify API keys are set

### "Error loading emails"
- Refresh the page (F5)
- Disconnect and reconnect Gmail
- Check Gmail permissions

### No Calendar Integration
- Ensure you authorized Calendar access during Gmail connection
- Check calendar permissions in Google Account

## Future Enhancements

- [ ] Email attachment support
- [ ] Batch email processing
- [ ] Custom reply templates
- [ ] Email scheduling
- [ ] Multi-account support
- [ ] Dark mode
- [ ] Email search and filtering
- [ ] Reply drafts auto-save
- [ ] Email signature customization
- [ ] Advanced analytics and insights

---

**Email Assistant Pro** | Built with Streamlit, LangGraph, and Gemini AI
