from .state import EmailState
from .calendar import create_event

KEYWORDS = ["interview", "meeting", "call", "schedule"]

def maybe_create_event(state: EmailState) -> EmailState:
    decision = state.get("human_decision", "")
    text = (state["subject"] + " " + state["body"]).lower()

    if decision in ("approved", "edited", "auto_approved"):
        if any(word in text for word in KEYWORDS):
            create_event(state["subject"])

    return state
