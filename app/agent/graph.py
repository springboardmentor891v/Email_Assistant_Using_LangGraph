"""
LangGraph State Graph for Email Assistant

This module defines the complete agent workflow using LangGraph's StateGraph.
It orchestrates the flow from triage → decision routing → appropriate action.
"""

from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent.triage import triage_email
from agent.react_loop import react_node


class AgentState(TypedDict):
    """Global state for the email agent"""
    email_subject: str
    email_body: str
    triage_decision: str
    react_result: Optional[Dict[str, Any]]
    final_output: str


def triage_node(state: AgentState) -> AgentState:
    """
    Triage node: Classifies the email into categories
    
    Returns:
        Updated state with triage_decision
    """
    print(f"\n{'='*60}")
    print(f"🔍 TRIAGE NODE")
    print(f"{'='*60}")
    
    decision = triage_email(
        subject=state["email_subject"],
        body=state["email_body"]
    )
    
    print(f"Decision: {decision}")
    print(f"{'='*60}\n")
    
    return {
        **state,
        "triage_decision": decision
    }


def ignore_node(state: AgentState) -> AgentState:
    """
    Handle ignored emails (spam, ads, newsletters)
    
    Returns:
        Updated state with final_output
    """
    print(f"\n{'='*60}")
    print(f"🗑️ IGNORE NODE")
    print(f"{'='*60}")
    print(f"Email marked as spam/promotional - no action taken")
    print(f"{'='*60}\n")
    
    return {
        **state,
        "final_output": f"Email '{state['email_subject']}' has been marked as spam/promotional and will be ignored."
    }


def hitl_node(state: AgentState) -> AgentState:
    """
    Human-in-the-Loop node: Marks email for human review
    
    Returns:
        Updated state with final_output
    """
    print(f"\n{'='*60}")
    print(f"👤 HUMAN-IN-THE-LOOP NODE")
    print(f"{'='*60}")
    print(f"Email flagged for human review")
    print(f"{'='*60}\n")
    
    return {
        **state,
        "final_output": (
            f"⚠️ Email '{state['email_subject']}' requires human review.\n"
            f"This email has been flagged for your attention. "
            f"Please review and take appropriate action."
        )
    }


def should_route(state: AgentState) -> Literal["ignore", "notify_human", "respond_act"]:
    """
    Conditional edge function: Routes based on triage decision
    
    Returns:
        Next node to visit
    """
    decision = state["triage_decision"]
    
    # Normalize decision (remove extra spaces, lowercase)
    decision = decision.strip().lower()
    
    # Map to exact node names
    if "ignore" in decision:
        return "ignore"
    elif "notify_human" in decision or "notify" in decision:
        return "notify_human"
    elif "respond_act" in decision or "respond" in decision or "act" in decision:
        return "respond_act"
    else:
        # Default to human review if unclear
        print(f"⚠️ Unknown triage decision: {decision}, routing to human review")
        return "notify_human"


def create_agent_graph() -> StateGraph:
    """
    Create and compile the full agent workflow graph
    
    Returns:
        Compiled LangGraph StateGraph
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("triage", triage_node)
    workflow.add_node("ignore", ignore_node)
    workflow.add_node("notify_human", hitl_node)
    workflow.add_node("respond_act", react_node)
    
    # Set entry point
    workflow.set_entry_point("triage")
    
    # Add conditional routing after triage
    workflow.add_conditional_edges(
        "triage",
        should_route,
        {
            "ignore": "ignore",
            "notify_human": "notify_human",
            "respond_act": "respond_act"
        }
    )
    
    # Connect all paths to END
    workflow.add_edge("ignore", END)
    workflow.add_edge("notify_human", END)
    workflow.add_edge("respond_act", END)
    
    # Compile with memory checkpointer
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


def run_agent(email_subject: str, email_body: str, thread_id: str = "default") -> Dict[str, Any]:
    """
    Run the email agent on a single email
    
    Args:
        email_subject: Subject of the email
        email_body: Body of the email
        thread_id: Unique thread ID for this conversation (for memory persistence)
        
    Returns:
        Final state after processing
    """
    # Create graph
    app = create_agent_graph()
    
    # Initial state
    initial_state = {
        "email_subject": email_subject,
        "email_body": email_body,
        "triage_decision": "",
        "react_result": None,
        "final_output": ""
    }
    
    # Run the graph
    config = {"configurable": {"thread_id": thread_id}}
    final_state = app.invoke(initial_state, config)
    
    return final_state


# Visualize the graph (optional, for debugging)
def visualize_graph():
    """Print ASCII visualization of the graph structure"""
    print("\n" + "="*60)
    print("EMAIL AGENT WORKFLOW GRAPH")
    print("="*60)
    print("""
    START
      ↓
    [TRIAGE]
      ↓
    Decision Routing
      ├─ ignore → [IGNORE] → END
      ├─ notify_human → [HITL] → END
      └─ respond_act → [REACT] → END
    """)
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test the graph
    visualize_graph()
    
    test_email = {
        "subject": "Meeting Request for Tomorrow",
        "body": "Hi, can we schedule a meeting tomorrow at 2 PM to discuss the project?"
    }
    
    print(f"\nTesting with email: {test_email['subject']}\n")
    result = run_agent(test_email["subject"], test_email["body"])
    
    print(f"\n{'='*60}")
    print(f"FINAL OUTPUT:")
    print(f"{'='*60}")
    print(result["final_output"])
    print(f"{'='*60}\n")
