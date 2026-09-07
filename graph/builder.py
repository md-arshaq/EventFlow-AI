"""
StateGraph Builder and Compilation Engine.
Constructs the complete compiled StateGraph with:
- Typed state
- Conditional branching
- Checkpointer short-term memory integration
- ASCII & Mermaid visualization utilities
"""
from langgraph.graph import StateGraph, START, END
from graph.state import EventState
from graph.router import router_node
from graph.nodes import (
    event_info_node,
    task_node,
    guest_node,
    budget_node,
    schedule_node,
    memory_node,
    general_node,
    response_node
)
from graph.conditional_edges import route_intent
from memory.checkpointer import get_checkpointer

# Singleton compiled graph instance
_compiled_graph = None


def build_event_graph():
    """
    Builds and compiles the StateGraph for event planning.
    """
    workflow = StateGraph(EventState)

    # 1. Add all graph nodes
    workflow.add_node("router", router_node)
    workflow.add_node("event_info_node", event_info_node)
    workflow.add_node("task_node", task_node)
    workflow.add_node("guest_node", guest_node)
    workflow.add_node("budget_node", budget_node)
    workflow.add_node("schedule_node", schedule_node)
    workflow.add_node("memory_node", memory_node)
    workflow.add_node("general_node", general_node)
    workflow.add_node("response_node", response_node)

    # 2. Add entry point: START -> router
    workflow.add_edge(START, "router")

    # 3. Add Conditional Edge from router to target node
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "event_info_node": "event_info_node",
            "task_node": "task_node",
            "guest_node": "guest_node",
            "budget_node": "budget_node",
            "schedule_node": "schedule_node",
            "memory_node": "memory_node",
            "general_node": "general_node"
        }
    )

    # 4. Normal edges: connect all specialized nodes to response_node
    workflow.add_edge("event_info_node", "response_node")
    workflow.add_edge("task_node", "response_node")
    workflow.add_edge("guest_node", "response_node")
    workflow.add_edge("budget_node", "response_node")
    workflow.add_edge("schedule_node", "response_node")
    workflow.add_edge("memory_node", "response_node")
    workflow.add_edge("general_node", "response_node")

    # 5. Connect response_node to END
    workflow.add_edge("response_node", END)

    # 6. Compile with Short-Term Memory Checkpointer
    checkpointer = get_checkpointer()
    compiled = workflow.compile(checkpointer=checkpointer)
    return compiled


def get_graph():
    """Returns singleton compiled graph instance."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_event_graph()
    return _compiled_graph


def reset_graph():
    """Resets the compiled graph singleton."""
    global _compiled_graph
    _compiled_graph = None
    return get_graph()


def get_graph_ascii() -> str:
    """Returns ASCII diagram string of the compiled graph."""
    graph = get_graph()
    try:
        return graph.get_graph().draw_ascii()
    except Exception:
        return """
           +-----------+
           |   START   |
           +-----+-----+
                 |
                 v
           +-----------+
           |  router   |
           +-----+-----+
          /   |   |   |   \\
         /    |   |   |    \\
        v     v   v   v     v
     [Event] [Tasks] [Guests] [Budget] [Schedule] [General]
        \\     |   |   |     /
         \\    |   |   |    /
          v   v   v   v   v
        +---------------+
        | response_node |
        +-------+-------+
                |
                v
           +-----------+
           |    END    |
           +-----------+
        """


def get_graph_mermaid() -> str:
    """Returns Mermaid markup for live interactive rendering."""
    graph = get_graph()
    try:
        return graph.get_graph().draw_mermaid()
    except Exception:
        return """
graph TD
    __start__([START]) --> router[Router Node]
    router -.->|event_info| event_info_node[Event Info Node]
    router -.->|tasks| task_node[Task Node (operator.add)]
    router -.->|guests| guest_node[Guest Node (operator.add)]
    router -.->|budget| budget_node[Budget Node]
    router -.->|schedule| schedule_node[Schedule Node]
    router -.->|memory| memory_node[Memory Node]
    router -.->|general| general_node[General Chat Node]

    event_info_node --> response_node[Response Node (Context Trimming)]
    task_node --> response_node
    guest_node --> response_node
    budget_node --> response_node
    schedule_node --> response_node
    memory_node --> response_node
    general_node --> response_node

    response_node --> __end__([END])
"""
