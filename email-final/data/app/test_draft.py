from app.graph import build_graph
from app.inbox import fetch_latest_email
def main():
    graph = build_graph()
    email = fetch_latest_email()

    if not email:
        print("📭 No new inbox emails found.")
        return


    result = graph.invoke(email)

    print("\n================ AGENT OUTPUT ================\n")

    print("Action decided:", result.get("action"))

    # Print reply only if it exists
    if result.get("reply"):
        print("\n✉️ Final Reply:\n")
        print(result["reply"])

    # Print human decision only if HITL ran
    if result.get("human_decision"):
        print("\n👤 Human decision:", result["human_decision"])

    if result.get("action") == "ignore":
        print("\n🗑️ Email ignored by agent.")

    elif result.get("action") == "notify_human":
        print("\n⚠️ Required human review.")

    print("\n==============================================\n")
    print("\nFinal decision:", result.get("human_decision"))

    if result.get("human_decision") == "auto_approved":
        print("✅ Auto-approved by system")



if __name__ == "__main__":
    main()
