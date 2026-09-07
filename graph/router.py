import re
from typing import Dict, Any
from graph.state import EventState
from memory.long_term_store import get_long_term_store
from graph.extractor import extract_all_event_data


def router_node(state: EventState) -> Dict[str, Any]:
    """
    Analyzes the latest user message:
    1. Extracts comprehensive structured event state across all dimensions.
    2. Classifies primary intent to route conditionally.
    3. Updates long-term user profile store if preferences are mentioned.
    """
    messages = state.get("messages", [])
    user_id = state.get("user_id", "default_user")
    store = get_long_term_store()

    if not messages:
        return {
            "intent": "general",
            "user_id": user_id,
            "long_term_profile": store.get_profile(user_id)
        }

    latest_msg = str(messages[-1].content)
    text_lower = latest_msg.lower()

    # Save personal preferences to long-term memory
    store.extract_and_save_preferences(latest_msg, user_id)
    profile = store.get_profile(user_id)

    # Perform comprehensive entity extraction from message
    extracted = extract_all_event_data(latest_msg)

    # Determine intent for conditional graph routing
    intent = "general"

    if re.search(r"\b(?:add task|my task|tasks?|todos?|action items?)\b", text_lower) or "tasks" in extracted:
        intent = "tasks"
    elif re.search(r"\b(?:guest list|add rahul|add ahmed|invite|attendees?)\b", text_lower) or "guest_list" in extracted:
        intent = "guests"
    elif re.search(r"\b(?:budget|costs?|prices?|how much|financial|breakdown|₹|rs\.?)\b", text_lower) or "budget" in extracted:
        intent = "budget"
    elif re.search(r"\b(?:schedule|agenda|timeline|starts? at|\d+\s*(?:am|pm)|clock)\b", text_lower) or "event_time" in extracted:
        intent = "schedule"
    elif re.search(r"\b(?:my name is|i prefer|my preference|remember that)\b", text_lower):
        intent = "memory"
    elif re.search(r"\b(?:planning|event|birthday|party|workshop|meetup|seminar|conference|gathering|people|guests|date|venue|location)\b", text_lower) or "event_type" in extracted:
        intent = "event_info"

    # Exclude list-reduced fields from router return so specialized nodes add them once
    router_state_updates = {k: v for k, v in extracted.items() if k not in ["tasks", "guest_list"]}

    result = {
        **router_state_updates,
        "intent": intent,
        "user_id": user_id,
        "long_term_profile": profile
    }

    return result
