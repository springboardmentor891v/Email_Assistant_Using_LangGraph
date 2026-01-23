"""
LangGraph State Graph - Production Email Workflow
Routes emails through triage with HITL for important messages
"""
from langgraph.graph import StateGraph, END, START
from agent.triage import triage_node
from agent.react_loop import react_node
from agent.hitl import human_approval
from typing import TypedDict, Optional, Dict, Any


class EmailState(TypedDict, total=False):
    email_subject: str
    email_body: str
    thread_id: str
    
    triage_decision: str
    intent: str
    
    react_result: Dict[str, Any]
    final_output: str
    status: str
    approved: bool


def route_after_triage(state: EmailState) -> str:
    """
    Route based on triage decision:
    - ignore: Skip processing
    - notify_human: Request approval before acting
    - respond_act: Auto-process with ReAct
    """
    decision = state.get("triage_decision", "").lower()
    
    if "ignore" in decision:
        return "ignore"
    elif "notify_human" in decision or "notify" in decision:
        return "notify_human"
    else:  # respond_act
        return "respond_act"


def ignore_node(state: EmailState):
    """Mark email as spam/promotional, no action"""
    state["final_output"] = f"Email ignored (spam/promotional)"
    state["status"] = "ignored"
    return state


def approval_node(state: EmailState):
    """Request human approval for important emails"""
    print("\n" + "="*70)
    print("⚠️  HUMAN APPROVAL REQUIRED")
    print("="*70)
    print(f"Subject: {state.get('email_subject', 'N/A')}")
    print(f"From: (check email)")
    print(f"Reason: Important email requiring review")
    print()
    
    approved = human_approval(
        action="review_and_respond",
        payload={
            "subject": state.get("email_subject"),
            "body_preview": state.get("email_body", "")[:200]
        }
    )
    
    state["approved"] = approved
    
    if approved:
        state["status"] = "approved_for_processing"
        # Continue to ReAct loop
    else:
        state["status"] = "rejected"
        state["final_output"] = "Email review rejected by human. No action taken."
    
    return state


def route_after_approval(state: EmailState) -> str:
    """Route after human approval"""
    if state.get("approved", False):
        return "react"
    else:
        return END


def build_graph():
    """Build the email processing workflow graph"""
    graph = StateGraph(EmailState)
    
    # Add nodes
    graph.add_node("triage", triage_node)
    graph.add_node("ignore", ignore_node)
    graph.add_node("approval", approval_node)
    graph.add_node("react", react_node)
    
    # Start with triage
    graph.add_edge(START, "triage")
    
    # Route after triage
    graph.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "ignore": "ignore",
            "notify_human": "approval",
            "respond_act": "react"
        }
    )
    
    # Ignore ends immediately
    graph.add_edge("ignore", END)
    
    # After approval, either go to react or end
    graph.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "react": "react",
            END: END
        }
    )
    
    # ReAct ends
    graph.add_edge("react", END)
    
    return graph.compile()


_graph = build_graph()


def run_agent(email_subject: str, email_body: str, thread_id: str):
    """Run the email processing agent"""
    return _graph.invoke({
        "email_subject": email_subject,
        "email_body": email_body,
        "thread_id": thread_id
    })


def visualize_graph():
    """Print ASCII visualization of the workflow"""
    print("\n" + "="*70)
    print("EMAIL WORKFLOW GRAPH")
    print("="*70)
    print("""
    START
      ↓
    [TRIAGE]
      ↓
    Decision Router:
      ├─ ignore → [IGNORE] → END
      ├─ notify_human → [HUMAN APPROVAL]
      │                      ├─ approved → [REACT] → END
      │                      └─ rejected → END
      └─ respond_act → [REACT] → END
    """)
    print("="*70 + "\n")
