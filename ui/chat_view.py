"""
Chat Interface Component for LangGraph Event Coordinator.
Renders conversation messages and manages user input dispatch to the compiled StateGraph.
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.builder import get_graph


def render_chat_view():
    """Renders the conversational chat interface for current thread."""
    thread_id = st.session_state.current_thread_id
    thread_title = st.session_state.threads.get(thread_id, thread_id)
    graph = get_graph()

    st.subheader(f"💬 Conversation: {thread_title}")
    st.caption(f"Active Thread ID: `{thread_id}` | Persistent State managed by LangGraph SQLite Checkpointer")

    # Retrieve current state from checkpointer
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.get_state(config)
    messages = state.values.get("messages", []) if state and state.values else []

    # Message Display Container
    chat_container = st.container(height=450)
    with chat_container:
        if not messages:
            st.info("👋 Welcome! Start planning your event. (e.g., *'I am planning a birthday party for 30 people on Dec 20.'*)")
        else:
            for msg in messages:
                if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
                    with st.chat_message("user"):
                        st.write(msg.content)
                elif isinstance(msg, AIMessage) or getattr(msg, "type", "") == "ai":
                    with st.chat_message("assistant"):
                        st.write(msg.content)

    # Chat Input Box
    user_input = st.chat_input("Type your event planning message or task...")
    if user_input:
        # Construct input payload
        input_payload = {
            "messages": [HumanMessage(content=user_input)],
            "user_id": "default_user"
        }

        # Invoke StateGraph with thread configuration
        with st.spinner("Processing through LangGraph nodes..."):
            try:
                result = graph.invoke(input_payload, config=config)
                st.session_state["last_result"] = result

                # Auto-update thread name if event_type was identified and title was generic
                event_type = result.get("event_type")
                if event_type:
                    from memory.threads_store import add_or_update_thread
                    current_title = st.session_state.threads.get(thread_id, "")
                    if "thread_" in current_title.lower() or current_title in ["New Thread", "Tech Workshop"]:
                        icon = "💻" if "dsa" in event_type.lower() or "tech" in event_type.lower() else "🎉"
                        add_or_update_thread(thread_id, f"{icon} {event_type}")

                st.rerun()
            except Exception as e:
                st.error(f"Error invoking graph: {e}")
