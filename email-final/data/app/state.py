from typing import TypedDict, Optional

class EmailState(TypedDict):
    sender: str
    subject: str
    body: str
    threadId:str
    action: Optional[str]
    reply: Optional[str]
    politeness_score: Optional[float]
    human_decision: Optional[str]   # 👈 NEW
    auto_approved: bool | None
