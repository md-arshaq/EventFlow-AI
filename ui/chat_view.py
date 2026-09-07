import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.builder import get_graph
from graph.state_operations import delete_single_message, delete_last_turn, clear_thread_messages


def render_chat_view():
    """Renders the conversational chat interface with message deletion options."""
    thread_id = st.session_state.current_thread_id
    thread_title = st.session_state.threads.get(thread_id, thread_id)
    graph = get_graph()

    # Header and Action Toolbar
    col_header, col_undo, col_clear = st.columns([5, 2, 2])
    with col_header:
        st.subheader(f"💬 Conversation: {thread_title}")
        st.caption(f"Active Thread ID: `{thread_id}` | Persistent SQLite Memory")

    with col_undo:
        if st.button("↩️ Undo Turn", help="Remove last user prompt and assistant response"):
            if delete_last_turn(thread_id):
                st.success("Last turn undone!")
                st.rerun()

    with col_clear:
        if st.button("🧹 Clear Chat", help="Clear all messages in this conversation thread"):
            if clear_thread_messages(thread_id):
                st.success("Thread messages cleared!")
                st.rerun()

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
            for idx, msg in enumerate(messages):
                msg_id = getattr(msg, "id", None) or f"msg_{idx}"
                if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
                    with st.chat_message("user"):
                        col_text, col_del = st.columns([12, 1])
                        with col_text:
                            st.write(msg.content)
                        with col_del:
                            if st.button("🗑️", key=f"del_{msg_id}_{idx}", help="Delete this message"):
                                delete_single_message(thread_id, msg_id)
                                st.rerun()
                elif isinstance(msg, AIMessage) or getattr(msg, "type", "") == "ai":
                    with st.chat_message("assistant"):
                        col_text, col_del = st.columns([12, 1])
                        with col_text:
                            st.write(msg.content)
                        with col_del:
                            if st.button("🗑️", key=f"del_{msg_id}_{idx}", help="Delete this message"):
                                delete_single_message(thread_id, msg_id)
                                st.rerun()

    # Chat Input Box
    user_input = st.chat_input("Type your event planning message or task...")
    if user_input:
        # Construct input payload with unique UUID ID
        input_payload = {
            "messages": [HumanMessage(content=user_input, id=str(uuid.uuid4()))],
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
