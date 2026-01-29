from langgraph.graph import StateGraph, END
from .state import EmailState
from .triage import triage_email
from .draft import draft_reply
from .hitl import human_in_loop
from .eval import evaluate_politeness
from .auto import auto_decide
from .send import send_if_approved
from .calendar_node import maybe_create_event

def build_graph():
    graph = StateGraph(EmailState)

    # Nodes
    graph.add_node("triage", triage_email)
    graph.add_node("draft", draft_reply)
    graph.add_node("hitl", human_in_loop)
    graph.add_node("eval", evaluate_politeness)
    graph.add_node("send", send_if_approved)
    graph.add_node("calendar", maybe_create_event)

    # Entry
    graph.set_entry_point("triage")

    # Routing
    graph.add_conditional_edges(
        "triage",
        lambda state: state["action"],
        {
            "ignore": END,
            "notify_human": "hitl",
            "respond": "draft",
        },
    )

    # Flow
    graph.add_edge("draft", "hitl")
    graph.add_edge("hitl", "eval")
    graph.add_edge("eval", END)
    graph.add_node("auto", auto_decide)
    graph.add_edge("hitl", "eval")
    graph.add_edge("eval", "auto")
    graph.add_edge("auto", END)
    graph.add_edge("auto", "send")
    graph.add_edge("send", END)
    graph.add_edge("send", "calendar")
    graph.add_edge("calendar", END)

    return graph.compile()
