from langsmith import traceable
from app.core.calender import create_event
from app.core.gmail_client import send_reply
from memoryStore import get_sender_history, save_email_memory

import json
import re

# ======================================================
# 🧠 AI DECISION NODE (LLM)
# ======================================================
@traceable(name="ai_decision_node", run_type="chain")
def ai_decision_node(state, prompt, llm):
    # FIX: Added .get() to prevent KeyError during Streamlit resume
    sender = state.get("sender", "Unknown")
    if not sender:
        return {"decision": state.get("decision", {})}

    # 🔁 FETCH MEMORY
    history = get_sender_history(sender)
    memory_text = ""

    if history:
        memory_text = "\nPAST INTERACTIONS WITH THIS SENDER:\n"
        for action, ts in history:
            memory_text += f"- {action} at {ts}\n"

    chain = prompt | llm
    response = chain.invoke({
        "subject": state.get("subject", ""),
        "sender": sender,
        "body": state.get("body", "") + memory_text
    })

    # Normalize model output
    content = response.content
    if isinstance(content, list):
        raw = "".join(part if isinstance(part, str) else part.get("text", "") for part in content)
    else:
        raw = content

    raw = raw.strip()
    raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE)

    try:
        decision = json.loads(raw)
    except Exception:
        decision = {"action": "reply", "reply": "Thank you for your email.", "event": {}}

    decision.setdefault("action", "reply")
    decision.setdefault("reply", "")
    decision.setdefault("event", {})

    return {"decision": decision}

# ======================================================
# 👤 HUMAN CONFIRMATION NODE (FIXED FOR UI)
# ======================================================
@traceable(name="human_confirmation_node", run_type="tool")
def human_confirmation_node(state):
    # FIX: Removed while loop and input(). 
    # Streamlit passes the 'final_reply' directly through update_state.
    return {"final_reply": state.get("final_reply")}

# ======================================================
# 🗓️ CALENDAR NODE (FACTORY)
# ======================================================
def calendar_node_factory(calendar_service):
    @traceable(name="calendar_node", run_type="tool")
    def calendar_node(state):
        event = state.get("decision", {}).get("event", {})
        if not event.get("date") or not event.get("start_time"):
            return {}

        try:
            start_dt = f"{event['date']}T{event['start_time']}:00"
            end_dt = f"{event['date']}T{event.get('end_time', event['start_time'])}:00"

            create_event(calendar_service, summary=event.get("title", "Meeting"),
                        description=state.get("body", ""), start=start_dt, end=end_dt)

            save_email_memory(sender=state.get("sender"), subject=state.get("subject"),
                            thread_id=state.get("thread_id"), action="schedule")
        except Exception as e:
            print(f"❌ Calendar Error: {e}")
        return {}
    return calendar_node

# ======================================================
# 📤 SEND EMAIL NODE (FACTORY)
# ======================================================
def send_node_factory(service):
    @traceable(name="send_email_node", run_type="tool")
    def send_node(state):
        # FIX: Added .get() for safety
        final_reply = state.get("final_reply")
        if final_reply:
            send_reply(service, state.get("sender"), state.get("subject"),
                       final_reply, state.get("thread_id"))

            save_email_memory(sender=state.get("sender"), subject=state.get("subject"),
                            thread_id=state.get("thread_id"), action="reply", reply=final_reply)
        return {}
    return send_node