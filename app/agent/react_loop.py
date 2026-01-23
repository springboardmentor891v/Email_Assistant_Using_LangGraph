"""
ReAct Loop (Reasoning + Acting) for Email Assistant

This module implements the reasoning engine that:
1. Analyzes the email and current context
2. Decides what action/tool to use
3. Executes the tool
4. Reasons about the result
5. Repeats until task is complete
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.tools import BaseTool
from dotenv import load_dotenv
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import tools
from tools.calendar_tools import ALL_CALENDAR_TOOLS
from tools.email_tools import ALL_EMAIL_TOOLS

load_dotenv()

# Initialize LLM for reasoning
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.3
)


class ReactState(TypedDict):
    """State for the ReAct loop"""
    email_subject: str
    email_body: str
    reasoning_history: List[str]
    actions_taken: List[Dict[str, Any]]
    final_response: str
    iterations: int


# Combine all tools
ALL_TOOLS = ALL_CALENDAR_TOOLS + ALL_EMAIL_TOOLS

# Create tool registry
TOOL_REGISTRY = {tool.name: tool for tool in ALL_TOOLS}


def get_tool_descriptions() -> str:
    """Generate descriptions of all available tools"""
    descriptions = []
    for tool in ALL_TOOLS:
        descriptions.append(f"- {tool.name}: {tool.description}")
    return "\n".join(descriptions)


# Reasoning prompt
reasoning_prompt = PromptTemplate(
    input_variables=["email_subject", "email_body", "reasoning_history", "actions_taken"],
    template="""You are an intelligent email assistant with access to tools.

Email to Handle:
Subject: {email_subject}
Body: {email_body}

Previous Reasoning:
{reasoning_history}

Actions Taken So Far:
{actions_taken}

Available Tools:
{tool_descriptions}

Your task is to decide the NEXT ACTION to take. You can:
1. Use a tool (specify tool name and arguments)
2. Complete the task (if you have enough information)

Think step by step:
1. What is the user requesting in this email?
2. What information do I have?
3. What do I still need to do?
4. Which tool (if any) should I use next?

Respond in this EXACT JSON format:
{{
    "reasoning": "Your step-by-step thinking",
    "action": "tool_name or COMPLETE",
    "tool_args": {{"arg1": "value1", "arg2": "value2"}},
    "response_message": "Final message to user (only if action is COMPLETE)"
}}

If you're using a tool, provide the exact arguments it needs.
If the task is complete, set action to "COMPLETE" and provide a response_message.
"""
)


def reason_next_action(state: ReactState) -> Dict[str, Any]:
    """
    Use LLM to reason about what action to take next
    
    Returns:
        Dictionary with reasoning, action, tool_args, and response_message
    """
    # Format history
    history_str = "\n".join(state["reasoning_history"]) if state["reasoning_history"] else "None"
    actions_str = json.dumps(state["actions_taken"], indent=2) if state["actions_taken"] else "None"
    
    # Create chain
    chain = reasoning_prompt | llm
    
    # Get reasoning
    response = chain.invoke({
        "email_subject": state["email_subject"],
        "email_body": state["email_body"],
        "reasoning_history": history_str,
        "actions_taken": actions_str,
        "tool_descriptions": get_tool_descriptions()
    })
    
    # Parse response
    try:
        # Extract JSON from response
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        decision = json.loads(content)
        return decision
    except Exception as e:
        print(f"Error parsing reasoning response: {e}")
        print(f"Raw response: {response.content}")
        # Fallback
        return {
            "reasoning": "Error in reasoning",
            "action": "COMPLETE",
            "tool_args": {},
            "response_message": "I apologize, but I encountered an error processing this email. Please handle it manually."
        }


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Execute a tool and return its result"""
    if tool_name not in TOOL_REGISTRY:
        return f"Error: Tool '{tool_name}' not found"
    
    tool = TOOL_REGISTRY[tool_name]
    
    try:
        result = tool.invoke(tool_args)
        return result
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"


def react_loop(email_subject: str, email_body: str, max_iterations: int = 5) -> Dict[str, Any]:
    """
    Main ReAct loop that reasons and acts on an email
    
    Args:
        email_subject: Subject of the email
        email_body: Body of the email
        max_iterations: Maximum number of reasoning-acting cycles (safety limit)
        
    Returns:
        Dictionary with final_response and execution trace
    """
    # Initialize state
    state: ReactState = {
        "email_subject": email_subject,
        "email_body": email_body,
        "reasoning_history": [],
        "actions_taken": [],
        "final_response": "",
        "iterations": 0
    }
    
    print(f"\n{'='*60}")
    print(f"🤖 REACT LOOP STARTED")
    print(f"{'='*60}")
    print(f"Email: {email_subject}\n")
    
    # Main loop
    while state["iterations"] < max_iterations:
        state["iterations"] += 1
        print(f"\n--- Iteration {state['iterations']}/{max_iterations} ---")
        
        # Reason about next action
        decision = reason_next_action(state)
        
        print(f"💭 Reasoning: {decision['reasoning']}")
        print(f"🎯 Action: {decision['action']}")
        
        # Record reasoning
        state["reasoning_history"].append(
            f"Iteration {state['iterations']}: {decision['reasoning']}"
        )
        
        # Check if complete
        if decision["action"] == "COMPLETE":
            state["final_response"] = decision.get("response_message", "Task completed.")
            print(f"✓ Task Complete!")
            break
        
        # Execute tool
        tool_name = decision["action"]
        tool_args = decision.get("tool_args", {})
        
        print(f"🔧 Executing: {tool_name} with args {tool_args}")
        
        result = execute_tool(tool_name, tool_args)
        
        print(f"📊 Result: {result[:200]}..." if len(result) > 200 else f"📊 Result: {result}")
        
        # Record action
        state["actions_taken"].append({
            "iteration": state["iterations"],
            "tool": tool_name,
            "args": tool_args,
            "result": result
        })
    
    # Safety: If max iterations reached
    if state["iterations"] >= max_iterations and not state["final_response"]:
        state["final_response"] = (
            "I've analyzed this email but reached my action limit. "
            "This may require human review."
        )
        print(f"\n⚠️ Max iterations reached!")
    
    print(f"\n{'='*60}")
    print(f"✓ REACT LOOP COMPLETED")
    print(f"{'='*60}\n")
    
    return {
        "final_response": state["final_response"],
        "iterations": state["iterations"],
        "actions_taken": state["actions_taken"],
        "reasoning_history": state["reasoning_history"]
    }


# For LangGraph integration
def react_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the ReAct loop
    
    Args:
        state: LangGraph state containing email_subject and email_body
        
    Returns:
        Updated state with react_result
    """
    result = react_loop(
        email_subject=state["email_subject"],
        email_body=state["email_body"]
    )
    
    return {
        **state,
        "react_result": result,
        "final_output": result["final_response"]
    }
