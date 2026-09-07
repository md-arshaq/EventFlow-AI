"""
Message trimming and context window optimization engine.
Implements token budget enforcement (MAX_CONTEXT_TOKENS) and collects
before/after metrics to display in UI.
"""
from typing import List, Tuple, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage
from utils.token_counter import count_message_tokens
from utils.filtering import filter_messages_by_intent


def trim_and_filter_messages(
    messages: List[BaseMessage],
    intent: str = "general",
    max_tokens: int = 1500,
    max_messages: int = 10
) -> Tuple[List[BaseMessage], Dict[str, Any]]:
    """
    Trims and filters a message list down to fit within a given token and message count budget.
    Preserves original state history while optimizing model context.

    Returns:
        (trimmed_messages, metrics_dict)
    """
    raw_msg_count = len(messages)
    raw_token_count = count_message_tokens(messages)

    if not messages:
        return [], {
            "messages_before": 0,
            "messages_after": 0,
            "tokens_before": 0,
            "tokens_after": 0,
            "reduction_percent": 0.0,
            "trimmed": False
        }

    # Step 1: Filter messages by intent
    filtered = filter_messages_by_intent(messages, intent)

    # Step 2: Separate System messages from conversation messages
    system_msgs = [m for m in filtered if isinstance(m, SystemMessage)]
    conversation_msgs = [m for m in filtered if not isinstance(m, SystemMessage)]

    # Step 3: Message count budget
    if len(conversation_msgs) > max_messages:
        conversation_msgs = conversation_msgs[-max_messages:]

    # Step 4: Token budget trimming (remove from oldest conversation message forward)
    candidate_msgs = system_msgs + conversation_msgs
    current_tokens = count_message_tokens(candidate_msgs)

    while current_tokens > max_tokens and len(conversation_msgs) > 2:
        # Drop the oldest non-system message
        conversation_msgs.pop(0)
        candidate_msgs = system_msgs + conversation_msgs
        current_tokens = count_message_tokens(candidate_msgs)

    final_msgs = candidate_msgs
    final_msg_count = len(final_msgs)
    final_token_count = count_message_tokens(final_msgs)

    reduction_pct = 0.0
    if raw_token_count > 0:
        reduction_pct = round(((raw_token_count - final_token_count) / raw_token_count) * 100, 1)

    metrics = {
        "messages_before": raw_msg_count,
        "messages_after": final_msg_count,
        "tokens_before": raw_token_count,
        "tokens_after": final_token_count,
        "reduction_percent": max(0.0, reduction_pct),
        "trimmed": raw_msg_count > final_msg_count or raw_token_count > final_token_count
    }

    return final_msgs, metrics
