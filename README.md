# Email Assistant Using LangGraph

An intelligent, autonomous email assistant built with **LangGraph** that proactively manages email workflows using advanced agentic AI capabilities.

## 🎯 Project Overview

This project implements a sophisticated AI agent that can:
- **Triage incoming emails** automatically (spam, important, actionable)
- **Take autonomous actions** using calendar and email tools
- **Route complex requests** to human review (Human-in-the-Loop)
- **Reason and act** using the ReAct (Reasoning + Acting) pattern
- **Maintain conversation state** with LangGraph's memory system

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Email Assistant Agent              │
├─────────────────────────────────────────────┤
│                                             │
│  START → [TRIAGE] → Decision Router        │
│               ├─ ignore → [IGNORE]          │
│               ├─ notify_human → [HITL]      │
│               └─ respond_act → [REACT]      │
│                              ↓               │
│                      ┌──────────────┐       │
│                      │  ReAct Loop  │       │
│                      │  - Reasoning │       │
│                      │  - Tool Call │       │
│                      │  - Execute   │       │
│                      └──────────────┘       │
│                                             │
└─────────────────────────────────────────────┘
```

## ✅ Milestone 1: Complete

### Implemented Features

#### 1. **Triage System** ([triage.py](file:///c:/Users/Fakruddin/Desktop/Infosys/Email_Assistant_Using_LangGraph/app/agent/triage.py))
- Gemini-powered email classification
- Three categories: `ignore`, `notify_human`, `respond_act`
- Conservative routing for safety

#### 2. **ReAct Loop** ([react_loop.py](file:///c:/Users/Fakruddin/Desktop/Infosys/Email_Assistant_Using_LangGraph/app/agent/react_loop.py))
- Reasoning engine with Gemini LLM
- Tool selection and execution
- Maximum iteration safety (5 iterations)
- Complete audit trail

#### 3. **Mock Calendar Tools** ([calendar_tools.py](file:///c:/Users/Fakruddin/Desktop/Infosys/Email_Assistant_Using_LangGraph/app/tools/calendar_tools.py))
- `get_available_slots(date)` - Check availability
- `schedule_meeting(...)` - Book meetings with validation
- `list_upcoming_meetings(days_ahead)` - View schedule

#### 4. **Email Tools** ([email_tools.py](file:///c:/Users/Fakruddin/Desktop/Infosys/Email_Assistant_Using_LangGraph/app/tools/email_tools.py))
- `send_email(to, subject, body)` - Mock email sending
- `draft_response(...)` - AI-powered response generation with multiple styles

#### 5. **LangGraph State Graph** ([graph.py](file:///c:/Users/Fakruddin/Desktop/Infosys/Email_Assistant_Using_LangGraph/app/agent/graph.py))
- Complete workflow orchestration
- Conditional routing logic
- Memory persistence with `MemorySaver`
- Thread-based conversation isolation

#### 6. **LangSmith Integration**
- Tracing infrastructure configured
- Ready for monitoring and debugging
- Project: `email-assistant`

## 📁 Project Structure

```
Email_Assistant_Using_LangGraph/
├── app/
│   ├── agent/
│   │   ├── triage.py          # Email classification
│   │   ├── react_loop.py      # ReAct reasoning engine
│   │   ├── graph.py           # LangGraph orchestration
│   │   ├── hitl.py            # Human-in-the-loop (placeholder)
│   │   └── memory.py          # Memory management (placeholder)
│   ├── tools/
│   │   ├── calendar_tools.py  # Mock calendar operations
│   │   └── email_tools.py     # Email handling tools
│   ├── main.py                # Main application entry
│   └── test_runner.py         # Test harness with output capture
├── evaluation/                # Future: evaluation datasets
├── notebook/                  # Jupyter notebooks for exploration
│   └── gmail_api.ipynb        # Gmail API exploration
├── .env                       # Environment variables (not in repo)
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
└── ProjectObjective.md        # Project goals and definitions
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/springboardmentor891v/Email_Assistant_Using_LangGraph.git
   cd Email_Assistant_Using_LangGraph
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   
   # Optional: LangSmith (for monitoring)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGCHAIN_API_KEY=your_langsmith_api_key_here
   LANGCHAIN_PROJECT=email-assistant
   ```

### Running the Application

**Basic demo:**
```bash
python app/main.py
```

**Test runner (saves output to file):**
```bash
python app/test_runner.py
```

## 🧪 Testing

The application includes test emails covering all three routing paths:

1. **Ignore Path** - Spam/promotional emails
2. **HITL Path** - Important emails requiring human decision
3. **ReAct Path** - Safe, actionable emails

Run tests with:
```bash
python app/test_runner.py
```

Results are displayed in console and saved to `test_output.txt`.

## 🛠️ Technologies Used

- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Stateful, multi-actor agent framework
- **[LangChain](https://github.com/langchain-ai/langchain)** - LLM application framework
- **[Google Gemini](https://deepmind.google/technologies/gemini/)** - LLM for reasoning and generation
- **[LangSmith](https://smith.langchain.com/)** - Monitoring and tracing (optional)
- **[Pydantic](https://docs.pydantic.dev/)** -  Data validation

## 📊 Current Status

### ✅ Completed (Milestone 1)
- [x] Email triage with Gemini
- [x] ReAct loop with reasoning engine
- [x] Mock calendar and email tools
- [x] LangGraph state graph orchestration
- [x] Memory persistence infrastructure
- [x] LangSmith tracing setup
- [x] End-to-end testing

### 🚧 Upcoming (Milestone 2+)
- [ ] Real Gmail API integration
- [ ] Google Calendar API integration
- [ ] Human-in-the-loop UI
- [ ] Persistent memory (SQLite/PostgreSQL)
- [ ] Evaluation suite with LLM-as-judge
- [ ] Real-world deployment
- [ ] Email polling/webhook integration

## 🎓 Learning Objectives

This project demonstrates:
1. **Proactive Triage** - AI analyzes emails before user interaction
2. **Persistent Memory** - Agent recalls context across sessions
3. **True Autonomy via HITL** - Safe automation with human oversight
4. **Robustness via Evaluation** - Testing and quality assurance
5. **Real-World Deployment** - Production-ready architecture

## 📝 Configuration

### Model Selection

The agent uses **Gemini 1.5 Pro** for reasoning. To change:

```python
# In triage.py, react_loop.py, email_tools.py
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",  # Change this
    temperature=0
)
```

### Tool Customization

Add new tools in `app/tools/`:

```python
from langchain.tools import tool

@tool
def your_custom_tool(arg: str) -> str:
    """Tool description"""
    # Implementation
    return result
```

Register in `react_loop.py`:
```python
from app.tools.your_tools import your_custom_tool

ALL_TOOLS = ALL_CALENDAR_TOOLS + ALL_EMAIL_TOOLS + [your_custom_tool]
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as part of the Springboard AI Engineering program
- Uses Google's Gemini API for language understanding
- Powered by LangChain and LangGraph frameworks

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**Last Updated:** January 23, 2026  
**Version:** 1.0.0 (Milestone 1 Complete)
