from .state import EmailState
from .db import save_email_interaction

def human_in_loop(state: EmailState) -> EmailState:
    print("\n========== HUMAN IN THE LOOP ==========\n")

    print("From:", state["sender"])
    print("Subject:", state["subject"])
    print("Body:\n", state["body"])

    ai_reply = state.get("reply")

    if ai_reply:
        print("\n--- Drafted Reply ---\n")
        print(ai_reply)

    print("\nChoose an action:")
    print("1️⃣ Approve")
    print("2️⃣ Edit")
    print("3️⃣ Reject")

    choice = input("\nEnter 1 / 2 / 3: ").strip()

    if choice == "1":
        state["human_decision"] = "approved"
        final_reply = ai_reply

    elif choice == "2":
        print("\n✏️ Enter your edited reply:\n")
        final_reply = input()
        state["reply"] = final_reply
        state["human_decision"] = "edited"

    else:
        state["human_decision"] = "rejected"
        final_reply = None
        state["reply"] = None

    # 🔐 SAVE TO DB + GET EMAIL ID
    email_id = save_email_interaction(
        sender=state["sender"],
        subject=state["subject"],
        body=state["body"],
        ai_reply=ai_reply,
        final_reply=final_reply,
        decision=state["human_decision"]
    )

    # 👇 STORE ID IN STATE FOR EVAL STEP
    state["email_id"] = email_id

    return state
