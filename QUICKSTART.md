# Quick Start Guide - Ambient Email Agent

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies (1 min)
```bash
cd c:\Users\Fakruddin\Desktop\Infosys\ambient-email-agent
pip install -r requirements.txt
```

### Step 2: Setup Environment Variables (1 min)
1. Copy `.env.example` to `.env`
2. Get Gemini API key from: https://makersuite.google.com/app/apikey
3. Paste it in `.env` file:
   ```
   GEMINI_API_KEY1=your_actual_api_key_here
   ```

### Step 3: Setup Google Cloud Credentials (3 min)

#### Quick Method:
1. Go to: https://console.cloud.google.com/
2. Create/Select a project
3. Click: "APIs & Services" → "Enable APIs" 
4. Enable: **Gmail API** and **Google Calendar API**
5. Click: "Credentials" → "Create Credentials" → "OAuth client ID"
6. Select: "Desktop app"
7. Download JSON file → Rename to `credentials.json`
8. Move to: `src/contents/credentials.json`

### Step 4: Run! 🎉
```bash
python main.py
```

First run will open browser for Google login. After that, it runs automatically!

---

## 📖 How It Works

When you run `python main.py`:

1. **Fetches** your latest email
2. **Analyzes** it using AI (Gemini)
3. **Categorizes** into:
   - 🗑️ **IGNORE** → Spam/Marketing (auto-ignored)
   - 🔔 **NOTIFY** → Important info (shows notification)
   - ✉️ **RESPOND** → Needs reply (creates draft)

4. **For emails needing response:**
   - Checks your calendar availability
   - Generates professional reply
   - Shows you the draft
   - Asks for approval
   - Learns from your feedback
   - Sends email & updates calendar

---

## 🎯 Usage Examples

### Review Draft Email
```
DRAFT PREVIEW:
To: friend@example.com
Subject: Re: Meeting Tomorrow
Body: Hi, I'd love to meet. I'm available at 2 PM...

Action (yes / no / replace / [type feedback]): _
```

**Your Options:**
- `yes` → Send email & add to calendar
- `no` → Cancel
- `replace` → Replace conflicting calendar event
- `make it more casual` → Agent rewrites with feedback
- `use "Hi" instead of "Hello"` → Learns preference forever

---

## 🛠️ Troubleshooting

### ❌ "credentials.json not found"
**Fix:** Download OAuth credentials from Google Cloud Console  
➜ Place in `src/contents/credentials.json`

### ❌ "GEMINI_API_KEY1 not set"
**Fix:** Create `.env` file with your API key  
➜ Get key from: https://makersuite.google.com/app/apikey

### ❌ "Access denied" during authentication
**Fix:** Make sure Gmail API and Calendar API are enabled in your Google Cloud project

### 🔄 Start Fresh
Delete `src/contents/token.json` and run again to re-authenticate

---

## 📂 Project Structure
```
ambient-email-agent/
├── main.py              ← Start here!
├── requirements.txt     ← Dependencies
├── .env                ← Your API keys (create this)
├── src/
│   ├── contents/
│   │   └── credentials.json  ← Google OAuth (download this)
│   ├── agent.py        ← Email triage & response logic
│   ├── gemini.py       ← AI integration
│   ├── tools.py        ← Gmail & Calendar tools
│   └── auth.py         ← Google authentication
└── data/
    └── agent_memory.db  ← Learns your preferences
```

---

## 🎓 Tips

1. **First Email:** Start with a simple email to test
2. **Feedback:** The more feedback you give, the smarter it gets
3. **Memory:** Your preferences are saved in `data/agent_memory.db`
4. **Customization:** Edit `main.py` line 10 to process more emails

---

## 📞 Need Help?

- Check full README: `README.md`
- Check project goals: `ProjectObjective.md`
- Review code: Look in `src/` folder
- Test in Jupyter: See `notebooks/` folder

---

**You're all set! Run `python main.py` and let the agent handle your emails! 🚀**
