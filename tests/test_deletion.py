"""
Automated unit tests for message deletion operations in LangGraph.
Verifies RemoveMessage functionality, undo last turn, and clearing thread history.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
from langchain_core.messages import HumanMessage
from graph.builder import get_graph, reset_graph
from memory.checkpointer import reset_checkpointer
from graph.state_operations import delete_single_message, delete_last_turn, clear_thread_messages


def test_delete_single_message():
    """Verify that delete_single_message removes a specific message by ID."""
    reset_checkpointer()
    graph = reset_graph()
    thread_id = "test_del_single"
    config = {"configurable": {"thread_id": thread_id}}

    msg1_id = str(uuid.uuid4())
    msg2_id = str(uuid.uuid4())

    # Send 2 messages
    graph.invoke({"messages": [HumanMessage(content="First message", id=msg1_id)], "user_id": "u1"}, config=config)
    graph.invoke({"messages": [HumanMessage(content="Second message", id=msg2_id)], "user_id": "u1"}, config=config)

    state = graph.get_state(config)
    initial_count = len(state.values.get("messages", []))
    assert initial_count >= 2

    # Delete first message
    success = delete_single_message(thread_id, msg1_id)
    assert success is True

    state_after = graph.get_state(config)
    messages_after = state_after.values.get("messages", [])
    remaining_ids = [getattr(m, "id", None) for m in messages_after]

    assert msg1_id not in remaining_ids
    assert len(messages_after) == initial_count - 1


def test_delete_last_turn():
    """Verify undo last turn removes the most recent exchange."""
    reset_checkpointer()
    graph = reset_graph()
    thread_id = "test_del_turn"
    config = {"configurable": {"thread_id": thread_id}}

    graph.invoke({"messages": [HumanMessage(content="Turn 1 prompt", id=str(uuid.uuid4()))], "user_id": "u1"}, config=config)
    graph.invoke({"messages": [HumanMessage(content="Turn 2 prompt", id=str(uuid.uuid4()))], "user_id": "u1"}, config=config)

    state_before = graph.get_state(config)
    count_before = len(state_before.values.get("messages", []))

    success = delete_last_turn(thread_id)
    assert success is True

    state_after = graph.get_state(config)
    count_after = len(state_after.values.get("messages", []))
    assert count_after < count_before


def test_clear_thread_messages():
    """Verify clearing all messages in a thread."""
    reset_checkpointer()
    graph = reset_graph()
    thread_id = "test_del_clear"
    config = {"configurable": {"thread_id": thread_id}}

    graph.invoke({"messages": [HumanMessage(content="Message A", id=str(uuid.uuid4()))], "user_id": "u1"}, config=config)
    graph.invoke({"messages": [HumanMessage(content="Message B", id=str(uuid.uuid4()))], "user_id": "u1"}, config=config)

    success = clear_thread_messages(thread_id)
    assert success is True

    state_after = graph.get_state(config)
    assert len(state_after.values.get("messages", [])) == 0


if __name__ == "__main__":
    test_delete_single_message()
    test_delete_last_turn()
    test_clear_thread_messages()
    print("All deletion tests passed successfully!")
