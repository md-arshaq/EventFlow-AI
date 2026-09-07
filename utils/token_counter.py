"""
Token estimation and counting utilities.
"""
from typing import List, Union
from langchain_core.messages import BaseMessage

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    _ENCODER = None


def count_string_tokens(text: str) -> int:
    """Estimates the token count of a given string."""
    if not text:
        return 0
    if _ENCODER is not None:
        try:
            return len(_ENCODER.encode(text))
        except Exception:
            pass
    # Fallback heuristic: 1 token ≈ 4 characters
    return max(1, len(text) // 4)


def count_message_tokens(messages: List[BaseMessage]) -> int:
    """Estimates the total token count of a list of BaseMessages."""
    total = 0
    for msg in messages:
        # Include role overhead (~3 tokens) + content tokens
        content_str = str(msg.content) if msg.content else ""
        total += 3 + count_string_tokens(content_str)
    return total
