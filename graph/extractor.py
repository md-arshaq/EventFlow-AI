"""
Comprehensive Event State Extraction Engine.
Extracts structured event attributes (type, date, time, location, guest count,
budget, tasks, guest names, schedule) from user messages.
"""
import re
from typing import Dict, Any, List


def extract_tasks_from_text(text: str) -> List[str]:
    """
    Extracts individual tasks from various input formats:
    - Comma-separated after 'tasks: ...' or 'Add the following tasks...:'
    - Quoted strings
    - Bullet points or numbered lists
    """
    tasks: List[str] = []

    # Format 1: Quoted items
    quoted_items = re.findall(r'["\']([^"\']+)["\']', text)
    if quoted_items and len(quoted_items) >= 2:
        return [q.strip() for q in quoted_items if len(q.strip()) > 2]

    # Format 2: "Add the following tasks ... : task 1, task 2, and task 3"
    task_section_match = re.search(
        r"(?:add\s+(?:the\s+following\s+)?tasks?(?:\s+to\s+the\s+event\s+plan)?|tasks?|todo|action items?)\s*[:\-]\s*(.+)",
        text,
        re.IGNORECASE
    )
    if task_section_match:
        raw_section = task_section_match.group(1).strip()
        # Clean trailing sentence punctuation if any
        raw_section = re.split(r"(?<=[.!?])\s+[A-Z]", raw_section)[0]

        # Check if contains bullet points or newlines
        if "\n" in raw_section:
            for line in raw_section.split("\n"):
                cleaned = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                if cleaned and len(cleaned) > 2:
                    tasks.append(cleaned)
        else:
            # Split on commas and 'and'
            parts = re.split(r",|\band\b", raw_section, flags=re.IGNORECASE)
            for p in parts:
                cleaned = p.strip(" \t\n\r.,;:-")
                if cleaned and len(cleaned) > 2:
                    tasks.append(cleaned)

        if tasks:
            return tasks

    # Format 3: Bullet points anywhere in text
    lines = text.split("\n")
    for line in lines:
        cleaned = line.strip()
        if cleaned.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")):
            item = re.sub(r"^[-*•\d.]+\s*", "", cleaned).strip()
            if item and len(item) > 2:
                tasks.append(item)

    if tasks:
        return tasks

    # Format 4: "Add book the venue to my tasks"
    single_match = re.search(r"(?:add|include)\s+(.+?)\s+(?:to\s+(?:my\s+)?tasks?|in\s+tasks?)", text, re.IGNORECASE)
    if single_match:
        item = single_match.group(1).strip(" \"'")
        if item and len(item) < 80:
            tasks.append(item)

    return tasks


def extract_all_event_data(text: str) -> Dict[str, Any]:
    """
    Comprehensive multi-field extractor for event details.
    """
    updates: Dict[str, Any] = {}
    text_lower = text.lower()

    # 1. Event Type
    if "dsa workshop" in text_lower:
        updates["event_type"] = "DSA Workshop"
    elif "workshop" in text_lower:
        updates["event_type"] = "Technical Workshop"
    elif "birthday" in text_lower:
        updates["event_type"] = "Birthday Party"
    elif "college meetup" in text_lower or "meetup" in text_lower:
        updates["event_type"] = "College Meetup"
    elif "conference" in text_lower:
        updates["event_type"] = "Conference"
    elif "seminar" in text_lower:
        updates["event_type"] = "Seminar"
    elif "gathering" in text_lower:
        updates["event_type"] = "Family Gathering"

    # 2. Guest / Student Count (e.g. "for 50 students", "30 people", "100 attendees")
    count_match = re.search(
        r"(?:for|around|approx|with|capacity for|seating for)?\s*(\d+)\s*(?:students|people|guests|attendees|persons|participants|members)",
        text,
        re.IGNORECASE
    )
    if count_match:
        try:
            updates["guest_count"] = int(count_match.group(1))
        except ValueError:
            pass

    # 3. Budget (e.g. "budget is ₹25,000", "₹20,000", "25000")
    budget_match = re.search(
        r"(?:budget|cost|spend|limit)\s*(?:is|of|around|approx)?\s*(?:₹|rs\.?|inr)?\s*(\d+[\d,.]*)",
        text,
        re.IGNORECASE
    )
    if budget_match:
        try:
            updates["budget"] = float(budget_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # 4. Event Date (e.g. "September 25th", "December 20", "25th Jan", "2026-10-15")
    months = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    date_match = re.search(
        rf"\b(?:on|date is|dated)?\s*({months}\s+\d{{1,2}}(?:st|nd|rd|th)?|\d{{1,2}}(?:st|nd|rd|th)?\s+{months}|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}})\b",
        text,
        re.IGNORECASE
    )
    if date_match:
        updates["event_date"] = date_match.group(1).strip()

    # 5. Event Time & Duration (e.g. "from 10 AM to 4 PM", "at 6 PM")
    time_match = re.search(
        r"(?:from\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*(?:to|-)\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)|\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))",
        text
    )
    if time_match:
        updates["event_time"] = time_match.group(1)

    # 6. Location / Venue Requirements
    venue_match = re.search(
        r"(?:prefer\s+(?:an?\s+)?|venue\s+is\s+|at\s+)([a-zA-Z\s]+(?:venue|hall|center|auditorium|club|campus|park|lounge|room)[^.,;]*)",
        text,
        re.IGNORECASE
    )
    if venue_match:
        updates["location"] = venue_match.group(1).strip()
    elif "indoor" in text_lower:
        updates["location"] = "Indoor Venue (Projector & Wi-Fi)"
    elif "outdoor" in text_lower:
        updates["location"] = "Outdoor Venue"

    # 7. Tasks extraction
    extracted_tasks = extract_tasks_from_text(text)
    if extracted_tasks:
        updates["tasks"] = extracted_tasks

    # 8. Guest Names
    guest_match = re.search(r"(?:add|invite)\s+([A-Za-z,\s]+?)\s+(?:to (?:the )?guest list|as guests)", text, re.IGNORECASE)
    if guest_match:
        raw_names = guest_match.group(1)
        names = re.split(r",|\band\b", raw_names, flags=re.IGNORECASE)
        g_list = [n.strip().capitalize() for n in names if len(n.strip()) > 1]
        if g_list:
            updates["guest_list"] = g_list

    return updates
