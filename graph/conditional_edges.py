"""
Conditional Routing Logic for LangGraph StateGraph.
Maps detected user intent to the appropriate graph processing node.
"""
from graph.state import EventState


def route_intent(state: EventState) -> str:
    """
    Conditional edge router function.
    Returns target node name based on state['intent'].
    """
    intent = state.get("intent", "general")

    mapping = {
        "event_info": "event_info_node",
        "tasks": "task_node",
        "guests": "guest_node",
        "budget": "budget_node",
        "schedule": "schedule_node",
        "memory": "memory_node",
        "general": "general_node"
    }

    return mapping.get(intent, "general_node")
