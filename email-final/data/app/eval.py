from .state import EmailState

def evaluate_politeness(state: EmailState) -> EmailState:
    """
    Politeness evaluation step.
    For now, it just passes the reply through safely.
    (AI-based scoring can be added later)
    """

    # ✅ Always read reply from state
    reply_text = state.get("reply", "")

    # Optional: store a placeholder politeness score
    state["politeness_score"] = 1.0  # max politeness for now

    # IMPORTANT: do NOT overwrite reply
    state["reply"] = reply_text

    return state
