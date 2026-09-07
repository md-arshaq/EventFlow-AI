"""
Persistent Conversation Threads Store.
Saves created and active thread metadata to threads.json so they survive browser reloads.
"""
import os
import json
from typing import Dict

THREADS_FILE = os.path.join(os.path.dirname(__file__), "threads.json")

DEFAULT_THREADS = {
    "thread_001": "🎂 Birthday Party",
    "thread_002": "🎓 College Meetup",
    "thread_003": "💻 DSA Workshop"
}


def load_threads() -> Dict[str, str]:
    """Loads threads dictionary from persistent JSON file."""
    if os.path.exists(THREADS_FILE):
        try:
            with open(THREADS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
        except Exception as e:
            print(f"Error loading threads: {e}")
    save_threads(DEFAULT_THREADS)
    return DEFAULT_THREADS.copy()


def save_threads(threads: Dict[str, str]):
    """Saves threads dictionary to persistent JSON file."""
    try:
        with open(THREADS_FILE, "w", encoding="utf-8") as f:
            json.dump(threads, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving threads: {e}")


def add_or_update_thread(thread_id: str, title: str) -> Dict[str, str]:
    """Adds or updates a thread title and persists."""
    threads = load_threads()
    threads[thread_id] = title
    save_threads(threads)
    return threads
