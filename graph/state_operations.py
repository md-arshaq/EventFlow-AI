"""
State Operations for LangGraph Message Management.
Implements granular and bulk message deletion using LangGraph's RemoveMessage sentinel.
"""
from typing import List, Optional
from langchain_core.messages import RemoveMessage, BaseMessage, HumanMessage, AIMessage
from graph.builder import get_graph


def delete_single_message(thread_id: str, message_id: str) -> bool:
    """
    Deletes a specific message from thread state using graph.update_state.
    """
    if not message_id:
        return False

    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # update_state applies the add_messages reducer with RemoveMessage without running nodes
        graph.update_state(config, {"messages": [RemoveMessage(id=message_id)]})
        return True
    except Exception as e:
        print(f"Error deleting message {message_id}: {e}")
        return False


def delete_last_turn(thread_id: str) -> bool:
    """
    Rolls back / undoes the most recent exchange (last user prompt and assistant response).
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state_obj = graph.get_state(config)

    if not state_obj or not state_obj.values:
        return False

    messages: List[BaseMessage] = state_obj.values.get("messages", [])
    if not messages:
        return False

    to_remove = []
    # Identify last AIMessage and preceding HumanMessage
    if isinstance(messages[-1], AIMessage) or getattr(messages[-1], "type", "") == "ai":
        to_remove.append(messages[-1])
        if len(messages) >= 2 and (isinstance(messages[-2], HumanMessage) or getattr(messages[-2], "type", "") == "human"):
            to_remove.append(messages[-2])
    else:
        to_remove.append(messages[-1])

    remove_sentinels = []
    for m in to_remove:
        msg_id = getattr(m, "id", None)
        if msg_id:
            remove_sentinels.append(RemoveMessage(id=msg_id))

    if remove_sentinels:
        try:
            graph.update_state(config, {"messages": remove_sentinels})
            return True
        except Exception as e:
            print(f"Error deleting last turn: {e}")
            return False

    return False


def clear_thread_messages(thread_id: str) -> bool:
    """
    Clears all messages from the active thread checkpointer while retaining event state.
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state_obj = graph.get_state(config)

    if not state_obj or not state_obj.values:
        return False

    messages: List[BaseMessage] = state_obj.values.get("messages", [])
    if not messages:
        return True

    remove_sentinels = []
    for m in messages:
        msg_id = getattr(m, "id", None)
        if msg_id:
            remove_sentinels.append(RemoveMessage(id=msg_id))

    if remove_sentinels:
        try:
            graph.update_state(config, {"messages": remove_sentinels})
            return True
        except Exception as e:
            print(f"Error clearing thread messages: {e}")
            return False

    return False
