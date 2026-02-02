def get_state_schema():
    from typing import TypedDict, Optional, Dict

    class EmailState(TypedDict):
        subject: str
        sender: str
        body: str
        thread_id: str
        decision: Dict
        final_reply: Optional[str]

    return EmailState
