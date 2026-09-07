"""
Comprehensive test suite verifying all LangGraph Module 2 requirements:
1. Graph compilation & routing
2. Non-default reducer accumulation (operator.add)
3. Thread-isolated Short-Term Memory
4. Cross-thread Long-Term Memory
5. Context trimming & token reduction
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from langchain_core.messages import HumanMessage
from graph.builder import get_graph, build_event_graph, reset_graph
from memory.checkpointer import reset_checkpointer
from memory.long_term_store import get_long_term_store
from utils.trimming import trim_and_filter_messages


def test_graph_compilation():
    """Verify that StateGraph builds and compiles without error."""
    graph = build_event_graph()
    assert graph is not None


def test_non_default_reducer_tasks():
    """Verify that the operator.add reducer accumulates tasks without overwriting."""
    reset_checkpointer()
    graph = reset_graph()
    config = {"configurable": {"thread_id": "test_thread_tasks"}}

    # Turn 1: Add first task
    graph.invoke({"messages": [HumanMessage(content='Add "Book venue" to my tasks.')], "user_id": "test_user"}, config=config)
    state = graph.get_state(config)
    assert "Book venue" in state.values.get("tasks", [])

    # Turn 2: Add second task
    graph.invoke({"messages": [HumanMessage(content='Add "Order food" to my tasks.')], "user_id": "test_user"}, config=config)
    state = graph.get_state(config)
    tasks = state.values.get("tasks", [])

    assert "Book venue" in tasks
    assert "Order food" in tasks
    assert len(tasks) >= 2


def test_thread_state_isolation():
    """Verify that Short-Term memory is strictly isolated between thread IDs."""
    reset_checkpointer()
    graph = reset_graph()

    # Thread A
    config_a = {"configurable": {"thread_id": "thread_A"}}
    graph.invoke({"messages": [HumanMessage(content="I am planning a birthday party for 30 people.")], "user_id": "test_user"}, config=config_a)

    # Thread B
    config_b = {"configurable": {"thread_id": "thread_B"}}
    graph.invoke({"messages": [HumanMessage(content="I am planning a conference for 200 people.")], "user_id": "test_user"}, config=config_b)

    state_a = graph.get_state(config_a)
    state_b = graph.get_state(config_b)

    assert state_a.values.get("guest_count") == 30
    assert state_b.values.get("guest_count") == 200


def test_long_term_memory_across_threads():
    """Verify that user profile preferences survive across different conversation threads."""
    store = get_long_term_store()
    store.update_profile("test_user_ltm", {"preferred_event_style": "outdoor", "name": "Arshaq"})

    graph = get_graph()
    config_new = {"configurable": {"thread_id": "new_isolated_thread"}}
    res = graph.invoke({"messages": [HumanMessage(content="What venue should I book?")], "user_id": "test_user_ltm"}, config=config_new)

    state = graph.get_state(config_new)
    assert state.values.get("long_term_profile", {}).get("preferred_event_style") == "outdoor"


def test_context_trimming_metrics():
    """Verify message trimming and token reduction calculation."""
    msgs = [
        HumanMessage(content="Turn 1: hello"),
        HumanMessage(content="Turn 2: party"),
        HumanMessage(content="Turn 3: venue"),
        HumanMessage(content="Turn 4: music"),
        HumanMessage(content="Turn 5: food"),
        HumanMessage(content="Turn 6: guests"),
        HumanMessage(content="Turn 7: budget"),
        HumanMessage(content="Turn 8: timeline"),
        HumanMessage(content="Turn 9: cleanup"),
        HumanMessage(content="Turn 10: goodbye")
    ]

    trimmed, metrics = trim_and_filter_messages(msgs, intent="budget", max_tokens=50, max_messages=4)
    assert len(trimmed) <= 4
    assert metrics["messages_before"] == 10
    assert metrics["messages_after"] <= 4
    assert metrics["tokens_after"] <= metrics["tokens_before"]


if __name__ == "__main__":
    test_graph_compilation()
    test_non_default_reducer_tasks()
    test_thread_state_isolation()
    test_long_term_memory_across_threads()
    test_context_trimming_metrics()
    print("All tests passed successfully!")
