"""
Message filtering utilities for LangGraph event coordinator.
Filters messages based on intent and relevance before LLM invocation.
"""
from typing import List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage


def filter_messages_by_intent(messages: List[BaseMessage], intent: str) -> List[BaseMessage]:
    """
    Filters conversation history to prioritize intent-relevant context
    while retaining recent conversational continuity.
    """
    if len(messages) <= 6:
        # For short histories, retain all messages
        return messages

    # Always keep system messages and the last 4 messages for conversational flow
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    recent_msgs = messages[-4:]
    older_msgs = messages[:-4]

    # Filter older messages based on intent keywords
    keywords = {
        "budget": ["budget", "cost", "price", "rupees", "rs", "₹", "spend", "expense", "venue", "food"],
        "guests": ["guest", "people", "attendee", "invite", "names", "who", "count"],
        "tasks": ["task", "todo", "action", "book", "order", "arrange", "deadline"],
        "schedule": ["time", "schedule", "agenda", "start", "pm", "am", "duration"],
        "event_info": ["type", "date", "theme", "birthday", "party", "meetup", "workshop", "location", "place"]
    }.get(intent, [])

    filtered_older = []
    for msg in older_msgs:
        if isinstance(msg, SystemMessage):
            continue
        content_lower = str(msg.content).lower()
        if not keywords or any(kw in content_lower for kw in keywords):
            filtered_older.append(msg)

    # Combine: System + Filtered Older + Recent turns (preserving ordering)
    result = system_msgs + [m for m in filtered_older if m not in system_msgs and m not in recent_msgs] + recent_msgs
    return result
