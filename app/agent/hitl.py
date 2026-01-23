def human_approval(action: str, payload: dict):
    print("\n⚠️ HUMAN APPROVAL REQUIRED")
    print(f"Action: {action}")
    print(f"Payload: {payload}")

    decision = input("Approve? (y/n): ").strip().lower()
    return decision == "y"
