"""
Typed State Definition for LangGraph Event Planning & Coordination Assistant.
Demonstrates:
- Standard message reducer (add_messages)
- Non-default custom reducers (operator.add for tasks and guest_list)
- Structured typed fields for event details and context optimization metadata.
"""
import operator
from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class EventState(TypedDict, total=False):
    """
    Typed graph state schema for event coordination.
    """
    # Standard reducer for conversation history
    messages: Annotated[List[BaseMessage], add_messages]

    # Non-default reducer for tasks: appends new tasks to existing list rather than overwriting
    tasks: Annotated[List[str], operator.add]

    # Non-default reducer for guests: appends new attendees
    guest_list: Annotated[List[str], operator.add]

    # Structured event attributes (default override reducer)
    event_type: Optional[str]
    event_name: Optional[str]
    event_date: Optional[str]
    event_time: Optional[str]
    location: Optional[str]
    guest_count: Optional[int]
    budget: Optional[float]
    schedule: Optional[List[str]]

    # Routing & Flow metadata
    intent: Optional[str]
    user_id: Optional[str]

    # Persistent long-term profile snapshot
    long_term_profile: Optional[Dict[str, Any]]

    # Trimming and context reduction statistics
    context_metadata: Optional[Dict[str, Any]]
