from app.core.calender import create_event
from app.core.gmail_client import send_reply
from memoryStore import get_sender_history, save_email_memory

# Decision Node
def ai_decision_node(state, prompt, llm):
    import json
    import re

    # 🔁 FETCH MEMORY
    history = get_sender_history(state["sender"])
    memory_text = ""

    if history:
        memory_text = "\nPAST INTERACTIONS WITH THIS SENDER:\n"
        for action, ts in history:
            memory_text += f"- {action} at {ts}\n"

    chain = prompt | llm
    response = chain.invoke({
        "subject": state["subject"],
        "sender": state["sender"],
        "body": state["body"] + memory_text
    })

    # Normalize content
    content = response.content
    if isinstance(content, list):
        raw = "".join(
            part if isinstance(part, str) else part.get("text", "")
            for part in content
        )
    else:
        raw = content

    raw = raw.strip()
    raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE)

    try:
        decision = json.loads(raw)
    except Exception:
        decision = {
            "action": "reply",
            "reply": "Thank you for your email. I’ll get back to you shortly.",
            "event": {}
        }

    # safety defaults
    decision.setdefault("action", "reply")
    decision.setdefault("reply", "")
    decision.setdefault("event", {})

    return {"decision": decision}

# human Confirmation Node
def human_confirmation_node(state):
    reply = state["decision"].get("reply")

    print("\n🤖 AI Draft Reply")
    print("-" * 60)
    print(reply)
    print("-" * 60)

    while True:
        choice = input("Send reply? (y / n / edit): ").strip().lower()

        if choice == "y":
            return {"final_reply": reply}

        if choice == "n":
            return {"final_reply": None}

        if choice == "edit":
            print("\n✏️ Enter edited reply (empty line to finish):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            return {"final_reply": "\n".join(lines)}
    

# Calender Node
def calendar_node_factory(calendar_service):
    def calendar_node(state):
        event = state.get("decision", {}).get("event", {})

        if not event.get("date") or not event.get("start_time"):
            print("⚠️ Incomplete event data. Skipping calendar.")
            return {}

        try:
            start_dt = f"{event['date']}T{event['start_time']}:00"
            end_dt = f"{event['date']}T{event.get('end_time', event['start_time'])}:00"

            create_event(
                calendar_service,
                summary=event.get("title", "Meeting"),
                description=state.get("body", ""),
                start=start_dt,
                end=end_dt
            )

            save_email_memory(
                sender=state["sender"],
                subject=state["subject"],
                thread_id=state["thread_id"],
                action="schedule"
            )

            print("🗓️ Event scheduled & remembered")

        except Exception as e:
            print(f"❌ Calendar Error: {e}")

        return {}

    return calendar_node

# Send Node
def send_node_factory(service):
    def send_node(state):
        if state.get("final_reply"):
            send_reply(
                service,
                state["sender"],
                state["subject"],
                state["final_reply"],
                state["thread_id"]
            )

            # 💾 SAVE TO MEMORY
            save_email_memory(
                sender=state["sender"],
                subject=state["subject"],
                thread_id=state["thread_id"],
                action="reply",
                reply=state["final_reply"]
            )

            print("✅ Reply sent & saved to memory")
        else:
            print("⏭️ Reply skipped")

        return {}

    return send_node
