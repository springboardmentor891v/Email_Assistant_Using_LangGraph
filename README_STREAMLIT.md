# 🎨 Streamlit AI Email Assistant

> **Beautiful, interactive email assistant with AI-powered features and calendar integration**

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-FF4B4B.svg)
![LangGraph](https://img.shields.io/badge/langgraph-0.0.40-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## ✨ What's This?

A **production-ready Streamlit web application** that transforms your Gmail into an AI-powered productivity hub with:

- 🎨 **Beautiful Modern UI** - Gradient-based design with smooth animations
- 📧 **Smart Email Management** - AI categorization, prioritization, and search
- 📅 **Calendar Intelligence** - Conflict detection and automated resolution
- 🤖 **LangGraph Workflows** - Advanced AI agent with memory persistence
- 💾 **Context Awareness** - Learns your patterns and preferences
- 🚀 **Real-time Updates** - Interactive dashboard with live metrics

---

## 🖼️ Screenshots

### Dashboard
Beautiful overview with real-time metrics, recent emails, and AI insights

### Email Manager
Advanced filtering, sorting, and AI-powered categorization

### Calendar View
Visual timeline of events grouped by date

### Conflict Resolution
Side-by-side comparison with AI-generated resolution emails

---

## 🚀 Quick Start (5 Minutes)

### 1. Install

```bash
# Clone or download the project
cd ambient-email-assistant

# Install dependencies
pip install -r requirements_streamlit.txt
```

### 2. Setup Google OAuth

**Must have:** `credentials.json` from Google Cloud Console

Follow [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) for detailed instructions:
1. Create Google Cloud Project
2. Enable Gmail API + Calendar API
3. Create OAuth 2.0 credentials
4. Download as `credentials.json`

### 3. Configure (Optional)

```bash
# Copy environment template
cp env.example .env

# Edit .env
# Add: OPENAI_API_KEY=sk-your-key-here (optional for AI features)
```

### 4. Run!

**Linux/Mac:**
```bash
./start_streamlit.sh
# or
streamlit run streamlit_app.py
```

**Windows:**
```batch
start_streamlit.bat
REM or
streamlit run streamlit_app.py
```

**Browser opens automatically at:** `http://localhost:8501`

---

## 📱 Features

### 🏠 Dashboard
- **Real-time Metrics**: Total emails, calendar events, conflicts, important
- **Recent Emails**: Quick preview of latest 8 emails with badges
- **AI Insights**: Smart suggestions and priorities
- **Today's Events**: Calendar snapshot
- **Quick Actions**: Refresh and AI workflow buttons

### 📧 Email Manager
- **Advanced Search**: Gmail query syntax support
- **Smart Filters**: All, Unread, Important, Calendar tabs
- **AI Categorization**: Work, personal, urgent, spam detection
- **Priority Scoring**: 0-10 scale based on content analysis
- **Sentiment Analysis**: Positive, neutral, negative
- **Full Details**: Read complete emails with threading

### 📅 Calendar Manager
- **Event Timeline**: View events for next 7-90 days
- **Grouped by Date**: Clean organization
- **Event Details**: Time, duration, location, attendees
- **Conflict Detection**: One-click scanning
- **Smart Scheduling**: Find free slots automatically

### ⚠️ Conflict Resolution
- **Automatic Detection**: Scans for overlapping meetings
- **Visual Comparison**: Side-by-side event details
- **Overlap Analysis**: Exact conflict duration
- **Alternative Times**: AI-powered free slot finding
- **Email Generation**: Professional resolution emails
- **One-click Drafts**: Save directly to Gmail

### ✍️ Compose
- **Rich Editor**: Clean, simple interface
- **Smart Reply**: Context from original email
- **AI Enhancement**: Professional, friendly, concise tones (coming soon)
- **Draft Saving**: Store in Gmail drafts
- **Direct Sending**: Send immediately

### 🤖 AI Workflow
- **Complete Analysis**: Emails + Calendar + Conflicts
- **Progress Tracking**: Real-time status updates
- **Smart Suggestions**: Action items and priorities
- **Auto-drafting**: Conflict resolution emails
- **Memory Persistence**: Learns over time

---

## 🎨 UI/UX Design

### Color Scheme
```css
Primary:   #00E5A0 (Mint Green)
Secondary: #00B8D4 (Cyan)
Accent:    #FF6B6B (Coral)
Warning:   #FFB800 (Amber)
Dark BG:   #0D0D0F
Card BG:   #1C1C21
```

### Design Elements
- ✨ Gradient backgrounds
- 🎯 Hover effects and animations
- 📊 Metric cards with stats
- 🏷️ Badge system (Unread, Important, Calendar)
- 📋 Color-coded cards
- 🎭 Smooth transitions
- 🖱️ Custom scrollbars
- 📱 Responsive layout

### Components
- **Metric Cards**: Gradient backgrounds, hover effects
- **Email Cards**: Border-left accent, badges
- **Conflict Cards**: Red theme for urgency
- **Calendar Cards**: Blue theme for events
- **Success Boxes**: Green theme for positive actions
- **Warning Boxes**: Yellow theme for attention items

---

## 🔧 Technical Stack

**Frontend:**
- Streamlit 1.29.0
- Custom CSS/HTML
- Plotly (optional charts)

**Backend:**
- Python 3.9+
- LangGraph 0.0.40 (workflow engine)
- LangChain (AI integration)

**APIs:**
- Gmail API (email operations)
- Google Calendar API (events)
- OpenAI API (AI features)

**Database:**
- SQLite (workflow checkpointing)
- Pickle (conversation memory)

---

## 📂 Project Structure

```
streamlit-email-assistant/
├── streamlit_app.py                 # Main Streamlit app ⭐
├── ambient_email_assistant_enhanced.py  # Core logic
├── requirements_streamlit.txt       # Dependencies
├── start_streamlit.sh              # Linux/Mac launcher
├── start_streamlit.bat             # Windows launcher
├── credentials.json                # Google OAuth (you add)
├── token.json                      # Auto-generated
├── .env                            # Environment config
├── .streamlit/
│   └── config.toml                 # Streamlit config
├── memory/
│   ├── checkpoints.db              # Workflow state
│   └── conversation_memory.pkl     # Long-term memory
└── docs/
    ├── STREAMLIT_GUIDE.md          # Detailed guide ⭐
    ├── GOOGLE_OAUTH_SETUP.md       # OAuth setup
    ├── README_ENHANCED.md          # Full docs
    └── QUICK_REFERENCE.md          # Code examples
```

---

## ⚙️ Configuration

### Streamlit Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#00E5A0"
backgroundColor = "#0D0D0F"
secondaryBackgroundColor = "#1C1C21"
textColor = "#FFFFFF"
font = "sans serif"

[server]
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false
```

### Environment Variables

Edit `.env`:

```env
# AI Features (optional)
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# App Settings
MAX_EMAILS=50
CALENDAR_DAYS_AHEAD=30
```

---

## 🎯 Usage Guide

### First Time Setup

1. **Launch App**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Connect Gmail**
   - Click "Connect to Gmail" in sidebar
   - Browser opens for authentication
   - Sign in with Google
   - Grant permissions (you may see "App not verified" - this is normal)
   - Click "Advanced" → "Go to app"
   - Approve all permissions

3. **Start Using**
   - Dashboard loads automatically
   - Click "Refresh" to fetch emails
   - Explore different pages

### Daily Workflow

**Morning:**
1. Open Dashboard
2. Check unread emails (metric card)
3. Review conflicts (if any)
4. Run AI Workflow for insights

**During Day:**
1. Check new emails as they arrive
2. Reply using Compose page
3. Resolve conflicts as they appear
4. Use AI suggestions for priorities

**End of Day:**
1. Clear important emails
2. Check tomorrow's calendar
3. Prepare conflict resolutions

---

## 💡 Tips & Tricks

### Performance

1. **Start Small**
   - Fetch 20-50 emails initially
   - Use search queries to filter
   - Increase as needed

2. **Use Filters**
   - Tabs: All, Unread, Important, Calendar
   - Search bar for specific queries
   - Sort by priority for AI-categorized emails

3. **Workflow Frequency**
   - Run AI workflow once per session
   - Refresh only when needed
   - Let memory learn your patterns

### Productivity

1. **Keyboard Focus**
   - Tab through forms
   - Enter to submit
   - Escape to close modals

2. **Quick Actions**
   - Sidebar refresh button (🔄)
   - Sidebar AI button (🤖)
   - Navigation shortcuts

3. **AI Features**
   - Enable with OPENAI_API_KEY
   - Categories: work, personal, urgent, spam
   - Priority: 0-10 scale
   - Sentiment: positive, neutral, negative

---

## 🐛 Troubleshooting

### App Won't Start

```bash
# Clear cache
streamlit cache clear

# Check dependencies
pip install -r requirements_streamlit.txt --upgrade

# Try again
streamlit run streamlit_app.py
```

### Authentication Issues

```bash
# Delete old token
rm token.json

# Restart app
streamlit run streamlit_app.py

# Re-authenticate
```

### CSS Not Loading

- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Check browser console (F12)
- Verify no ad blockers interfering

### AI Features Not Working

1. Check `.env` has `OPENAI_API_KEY`
2. Verify key is correct (starts with `sk-`)
3. Ensure OpenAI account has credits
4. Restart Streamlit

### Slow Performance

1. Reduce MAX_EMAILS in settings
2. Use specific search queries
3. Clear Streamlit cache
4. Close unused browser tabs

---

## 🚀 Advanced Usage

### Custom Queries

Gmail search syntax in Email Manager:

```
is:unread                    # Unread only
from:boss@company.com        # From specific sender
after:2024/01/01            # Date range
has:attachment               # With attachments
subject:meeting              # Subject contains
is:important OR is:starred   # Important or starred
```

### Bulk Operations

```python
# In workflow, process many emails
for email in st.session_state.emails:
    if email.is_unread and email.priority_score > 8:
        # Handle urgent emails
        pass
```

### Custom Filters

Add new filter tabs in Email Manager section:

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📬 All", 
    "🔵 Unread", 
    "⭐ Important", 
    "📅 Calendar",
    "🆕 Custom"  # Your new tab
])
```

---

## 📊 Analytics (Future)

Coming soon:
- Email volume charts
- Response time analytics
- Calendar utilization
- AI accuracy metrics
- Productivity insights

---

## 🔒 Security & Privacy

### What's Safe

✅ **Your data never leaves your control**
- OAuth tokens stored locally
- No data sent to external servers
- Session-based memory only
- Google's security standards

### What You Control

✅ **Full transparency**
- Open source code
- Review all API calls
- Audit permissions
- Revoke access anytime

### Best Practices

1. **Credentials**
   - Never commit `credentials.json`
   - Use `.gitignore` properly
   - Rotate OAuth tokens periodically

2. **API Keys**
   - Store in `.env` only
   - Never hardcode in files
   - Use different keys for dev/prod

3. **Access**
   - Review app permissions regularly
   - Revoke at: https://myaccount.google.com/permissions
   - Re-authenticate when suspicious

---

## 📚 Documentation

- **[STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)** - Complete Streamlit guide
- **[GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md)** - OAuth setup
- **[README_ENHANCED.md](README_ENHANCED.md)** - Full documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Code examples
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Setup instructions

---

## 🤝 Contributing

Contributions welcome!

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📄 License

MIT License - see LICENSE file

---

## 🎉 You're Ready!

Start the beautiful AI email assistant:

```bash
streamlit run streamlit_app.py
```

Navigate to **http://localhost:8501** and experience the future of email management! 🚀

---

## 🆘 Need Help?

- 📖 Check [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
- 🐛 Review error messages in terminal
- 🔍 Check browser console (F12)
- 📧 Verify all files are present
- 🔐 Test authentication separately

---

## ⭐ Features Roadmap

**v1.0** (Current)
- ✅ Beautiful UI/UX
- ✅ Gmail integration
- ✅ Calendar sync
- ✅ Conflict detection
- ✅ AI workflows

**v2.0** (Planned)
- [ ] Charts and analytics
- [ ] Email templates
- [ ] Scheduled sending
- [ ] Team collaboration
- [ ] Mobile responsive

**v3.0** (Future)
- [ ] Multi-account support
- [ ] Plugin system
- [ ] Advanced automation
- [ ] Integration marketplace

---

**Made with ❤️ using Streamlit & LangGraph**

*Last updated: 2024*
