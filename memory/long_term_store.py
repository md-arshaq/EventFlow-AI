"""
Long-Term Memory Store for cross-thread user profile persistence.
Maintains persistent user preferences (e.g. style, typical budget, name)
that survive across independent conversation threads.
"""
import os
import json
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

STORE_FILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")


class UserProfile(BaseModel):
    """Schema for persistent Long-Term User Profile."""
    name: Optional[str] = "Arshaq"
    preferred_event_style: Optional[str] = "outdoor"
    typical_budget: Optional[float] = 20000.0
    dietary_preferences: Optional[str] = None
    notes: Optional[str] = "Prefers tech-focused or interactive social gatherings."


class LongTermMemoryStore:
    """Manages persistent key-value profile storage independent of conversation threads."""

    def __init__(self, persistence_file: str = STORE_FILE_PATH):
        self.persistence_file = persistence_file
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
            except Exception:
                self.profiles = {}
        if "default_user" not in self.profiles:
            self.profiles["default_user"] = UserProfile().model_dump()
            self._save()

    def _save(self):
        try:
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Error persisting long term store: {e}")

    def get_profile(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Retrieves profile dictionary for a given user."""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile().model_dump()
            self._save()
        return self.profiles[user_id]

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates specific fields in user's long-term profile."""
        profile = self.get_profile(user_id)
        for k, v in updates.items():
            if v is not None and v != "":
                profile[k] = v
        self.profiles[user_id] = profile
        self._save()
        return profile

    def extract_and_save_preferences(self, text: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Heuristic / regex extraction of long-term preferences from conversational text.
        """
        text_lower = text.lower()
        updates = {}

        # Name extraction
        name_match = re.search(r"my name is ([a-zA-Z]+)", text, re.IGNORECASE)
        if name_match:
            updates["name"] = name_match.group(1).capitalize()

        # Preferred style extraction
        if "outdoor" in text_lower:
            updates["preferred_event_style"] = "outdoor"
        elif "indoor" in text_lower:
            updates["preferred_event_style"] = "indoor"
        elif "rooftop" in text_lower:
            updates["preferred_event_style"] = "rooftop"
        elif "hall" in text_lower:
            updates["preferred_event_style"] = "hall / banquet"

        # Typical budget extraction
        budget_match = re.search(r"(?:budget|spend|cost)\s*(?:around|is|of|approx)?\s*(?:₹|rs\.?|inr)?\s*(\d+[\d,.]*)", text, re.IGNORECASE)
        if budget_match:
            try:
                num_str = budget_match.group(1).replace(",", "")
                updates["typical_budget"] = float(num_str)
            except ValueError:
                pass

        if updates:
            return self.update_profile(user_id, updates)
        return self.get_profile(user_id)


# Global singleton instance
_long_term_store_instance = None


def get_long_term_store() -> LongTermMemoryStore:
    global _long_term_store_instance
    if _long_term_store_instance is None:
        _long_term_store_instance = LongTermMemoryStore()
    return _long_term_store_instance
