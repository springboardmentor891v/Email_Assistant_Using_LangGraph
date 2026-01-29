from .state import EmailState

AUTO_APPROVE_THRESHOLD = 8.0

def auto_decide(state: EmailState) -> EmailState:
    score = state.get("politeness_score")

    # If no score (ignore / rejected), do nothing
    if score is None:
        return state

    if score >= AUTO_APPROVE_THRESHOLD:
        state["human_decision"] = "auto_approved"
    else:
        state["human_decision"] = state.get("human_decision", "needs_review")

    return state
