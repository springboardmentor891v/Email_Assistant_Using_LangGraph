from app.agent.nodes import ai_decision_node, calendar_node_factory, human_confirmation_node, send_node_factory
from app.agent.states import get_state_schema
from app.core.llm import load_llm
from app.core.prompt import build_email_prompt


def build_email_graph(user_prompt: str, service, calendar_service):
    from langgraph.graph import StateGraph, END

    EmailState = get_state_schema()
    llm = load_llm()
    prompt = build_email_prompt(user_prompt)

    graph = StateGraph(EmailState)

    graph.add_node("ai_decision", lambda s: ai_decision_node(s, prompt, llm))
    graph.add_node("human_confirm", human_confirmation_node)
    graph.add_node("send", send_node_factory(service))
    graph.add_node("calendar", calendar_node_factory(calendar_service))

    graph.set_entry_point("ai_decision")

    def router(state):
        return state.get("decision", {}).get("action", "reply")

    graph.add_conditional_edges(
        "ai_decision",
        router,
        {
            "reply": "human_confirm",
            "schedule": "calendar",
            "ignore": END
        }
    )

    graph.add_edge("human_confirm", "send")
    graph.add_edge("send", END)
    graph.add_edge("calendar", END)

    return graph.compile()
