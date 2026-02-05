import os
from langsmith import traceable

def run_with_tracing(agent, state):
    @traceable(name="Email Agent Run")
    def _run():
        return agent.invoke(state)

    return _run()
