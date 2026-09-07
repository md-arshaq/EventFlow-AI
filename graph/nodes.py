"""
Graph Processing Nodes for Event Planning Assistant.
Implements domain-specific state extractors and the unified context-trimmed Response Node.
"""
import re
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from graph.state import EventState
from utils.trimming import trim_and_filter_messages
from utils.llm_factory import get_llm


def event_info_node(state: EventState) -> Dict[str, Any]:
    """Extracts high-level event details such as event type, date, location, and guest count."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    text = str(messages[-1].content)
    text_lower = text.lower()
    updates: Dict[str, Any] = {}

    # Event Type
    if "birthday" in text_lower:
        updates["event_type"] = "Birthday Party"
    elif "workshop" in text_lower:
        updates["event_type"] = "Workshop"
    elif "meetup" in text_lower:
        updates["event_type"] = "College Meetup"
    elif "seminar" in text_lower:
        updates["event_type"] = "Seminar"
    elif "conference" in text_lower:
        updates["event_type"] = "Conference"
    elif "gathering" in text_lower:
        updates["event_type"] = "Family Gathering"

    # Guest Count extraction (e.g. "for 30 people", "50 guests", "100 attendees")
    count_match = re.search(r"(?:for|around|approx|with)?\s*(\d+)\s*(?:people|guests|attendees|persons|members)", text, re.IGNORECASE)
    if count_match:
        try:
            updates["guest_count"] = int(count_match.group(1))
        except ValueError:
            pass

    # Date extraction (e.g. "December 20", "on 25th Jan", "tomorrow")
    date_match = re.search(r"(?:on|date is|for)\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    if date_match:
        updates["event_date"] = date_match.group(1)

    # Location extraction
    loc_match = re.search(r"(?:at|venue is|location is|in)\s+([A-Z][a-zA-Z\s]+(?:Hall|Park|Auditorium|Center|Club|Hotel|Lounge|Campus))", text)
    if loc_match:
        updates["location"] = loc_match.group(1).strip()

    return updates


from graph.extractor import extract_tasks_from_text


def task_node(state: EventState) -> Dict[str, Any]:
    """
    Extracts new tasks and returns them in a list.
    The 'operator.add' reducer automatically appends them to existing tasks!
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    text = str(messages[-1].content)
    new_tasks = extract_tasks_from_text(text)

    if not new_tasks:
        new_tasks = ["Coordinate general event logistics"]

    # Returning {"tasks": new_tasks} triggers non-default operator.add reducer
    return {"tasks": new_tasks}


def guest_node(state: EventState) -> Dict[str, Any]:
    """
    Extracts guest names and adds them to guest list using operator.add reducer.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    text = str(messages[-1].content)
    new_guests: List[str] = []

    # Pattern: "Add Rahul and Ahmed to guest list"
    guest_match = re.search(r"(?:add|invite)\s+([A-Za-z,\s]+?)\s+(?:to (?:the )?guest list|as guests)", text, re.IGNORECASE)
    if guest_match:
        raw_names = guest_match.group(1)
        names = re.split(r",|\band\b", raw_names, flags=re.IGNORECASE)
        for n in names:
            name_clean = n.strip()
            if name_clean and len(name_clean) > 1:
                new_guests.append(name_clean.capitalize())

    # Direct name lists if no match
    if not new_guests:
        words = [w.strip(" ,.") for w in text.split()]
        known_samples = ["Rahul", "Ahmed", "Priya", "Sara", "David", "Ananya", "Rohan"]
        for w in words:
            if w.capitalize() in known_samples and w.capitalize() not in new_guests:
                new_guests.append(w.capitalize())

    updates: Dict[str, Any] = {}
    if new_guests:
        updates["guest_list"] = new_guests

    # Also update guest count if mentioned
    count_match = re.search(r"(\d+)\s*(?:people|guests|attendees)", text, re.IGNORECASE)
    if count_match:
        try:
            updates["guest_count"] = int(count_match.group(1))
        except ValueError:
            pass

    return updates


def budget_node(state: EventState) -> Dict[str, Any]:
    """Extracts total event budget and produces planning allocations."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    text = str(messages[-1].content)
    budget_match = re.search(r"(?:budget|cost|spend|limit)\s*(?:is|of|around|approx)?\s*(?:₹|rs\.?|inr)?\s*(\d+[\d,.]*)", text, re.IGNORECASE)

    if budget_match:
        try:
            num_val = float(budget_match.group(1).replace(",", ""))
            return {"budget": num_val}
        except ValueError:
            pass

    return {}


def schedule_node(state: EventState) -> Dict[str, Any]:
    """Extracts start time and generates schedule timeline outline."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    text = str(messages[-1].content)
    time_match = re.search(r"(?:starts? at|time is|at)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))", text)
    if time_match:
        return {
            "event_time": time_match.group(1),
            "schedule": [
                f"{time_match.group(1)} - Guest Arrival & Welcome",
                "30 mins later - Main Activity / Opening",
                "90 mins later - Catering & Refreshments",
                "Final hour - Wrap-up & Networking"
            ]
        }
    return {}


def memory_node(state: EventState) -> Dict[str, Any]:
    """Node explicitly confirming preference sync into Long-Term profile."""
    return {}


def general_node(state: EventState) -> Dict[str, Any]:
    """Pass-through for general chat & planning brainstorming."""
    return {}


def response_node(state: EventState) -> Dict[str, Any]:
    """
    Unified response generation node.
    - Applies message filtering and trimming (MAX_CONTEXT_TOKENS).
    - Incorporates structured state + Long-Term user profile into prompt.
    - Collects before/after context metrics for visible UI proof.
    - Queries LLM (Gemini or DemoChatModel fallback).
    """
    messages = state.get("messages", [])
    intent = state.get("intent", "general")
    long_term = state.get("long_term_profile") or {}

    # Step 1: Trim & Filter context for model invocation
    trimmed_messages, metrics = trim_and_filter_messages(
        messages=messages,
        intent=intent,
        max_tokens=1500,
        max_messages=8
    )

    # Step 2: Formulate System Instruction including state and Long-Term profile
    profile_info = []
    if long_term.get("name"):
        profile_info.append(f"User Name: {long_term['name']}")
    if long_term.get("preferred_event_style"):
        profile_info.append(f"Preferred Event Style: {long_term['preferred_event_style']}")
    if long_term.get("typical_budget"):
        profile_info.append(f"Typical Budget: ₹{long_term['typical_budget']:,.0f}")

    event_summary = []
    if state.get("event_type"):
        event_summary.append(f"Event Type: {state['event_type']}")
    if state.get("guest_count"):
        event_summary.append(f"Guests: {state['guest_count']}")
    if state.get("event_date"):
        event_summary.append(f"Date: {state['event_date']}")
    if state.get("event_time"):
        event_summary.append(f"Time: {state['event_time']}")
    if state.get("budget"):
        event_summary.append(f"Budget: ₹{state['budget']:,.0f}")
    if state.get("tasks"):
        event_summary.append(f"Tasks: {', '.join(state['tasks'])}")
    if state.get("guest_list"):
        event_summary.append(f"Guest List: {', '.join(state['guest_list'])}")

    system_prompt = (
        "You are an expert AI Event Planning & Coordination Assistant.\n"
        "Help the user coordinate details like venues, budgets, guest lists, schedules, and tasks.\n\n"
        f"--- LONG-TERM USER PROFILE (Persistent across threads) ---\n"
        f"{chr(10).join(profile_info) if profile_info else 'No long-term preferences stored yet.'}\n\n"
        f"--- CURRENT EVENT STATE (Short-term thread memory) ---\n"
        f"{chr(10).join(event_summary) if event_summary else 'No event details recorded yet.'}\n\n"
        "Guidelines:\n"
        "1. Be friendly, structured, and proactive.\n"
        "2. When recommending venues or plans, acknowledge long-term preferences (like outdoor preference) if relevant.\n"
        "3. Keep responses concise and clear."
    )

    # Prepend SystemMessage to trimmed conversation
    model_input = [SystemMessage(content=system_prompt)] + [
        m for m in trimmed_messages if not isinstance(m, SystemMessage)
    ]

    # Step 3: Invoke LLM
    llm = get_llm()
    try:
        raw_res = llm.invoke(model_input)
        content = raw_res.content
        if isinstance(content, list):
            # Extract text blocks
            text_pieces = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_pieces.append(item["text"])
                elif isinstance(item, str):
                    text_pieces.append(item)
        import uuid
        response = AIMessage(content=cleaned_text, id=str(uuid.uuid4()))
    except Exception as e:
        import uuid
        response = AIMessage(content=f"Error communicating with LLM ({e}). Falling back to state response.", id=str(uuid.uuid4()))

    return {
        "messages": [response],
        "context_metadata": metrics
    }
