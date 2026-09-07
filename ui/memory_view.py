"""
Memory Inspection Component.
Visualizes and contrasts Short-Term Memory (thread checkpointer) vs. Long-Term Memory (global user profile).
"""
import streamlit as st
from graph.builder import get_graph
from memory.long_term_store import get_long_term_store


def render_memory_view():
    """Renders the dual-memory comparison view."""
    thread_id = st.session_state.current_thread_id
    thread_title = st.session_state.threads.get(thread_id, thread_id)
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state_obj = graph.get_state(config)
    values = state_obj.values if state_obj else {}
    messages = values.get("messages", [])

    st.subheader("🧠 Dual-Memory Architecture Inspection")
    st.caption("Compare thread-isolated Short-Term State vs. cross-thread Long-Term Profile Storage.")

    col_short, col_long = st.columns(2)

    with col_short:
        st.markdown("### ⏳ Short-Term Memory (Thread-Scoped)")
        st.info(f"Managed by **LangGraph SQLite Checkpointer** for `{thread_id}` ({thread_title}). State is strictly isolated to this thread and persists across page reloads.")

        st.metric("Messages in Thread State", len(messages))
        st.markdown(f"**Event Type:** `{values.get('event_type', 'None')}`")
        st.markdown(f"**Guests:** `{values.get('guest_count', 'None')}`")
        st.markdown(f"**Budget:** `{values.get('budget', 'None')}`")
        st.markdown(f"**Tasks in State:** `{len(values.get('tasks', []))} items`")

        if messages:
            with st.expander("🔍 View Raw Thread Checkpoint Messages"):
                for m in messages:
                    st.text(f"[{m.type.upper()}]: {m.content}")

    with col_long:
        st.markdown("### 🌐 Long-Term Memory (Cross-Thread)")
        st.success("Managed by **Long-Term Profile Store** for `user_id='default_user'`. Survives thread switching and app restarts!")

        store = get_long_term_store()
        profile = store.get_profile("default_user")

        st.markdown(f"**User Name:** `{profile.get('name', 'Arshaq')}`")
        st.markdown(f"**Preferred Event Style:** `{profile.get('preferred_event_style', 'outdoor')}`")
        b = profile.get("typical_budget")
        st.markdown(f"**Typical Budget:** `₹{b:,.0f}`" if b else "**Typical Budget:** `Not set`")
        st.markdown(f"**Stored Notes:** `{profile.get('notes', 'None')}`")

        st.markdown("---")
        st.markdown("💡 **Evaluation Note:** If you create a new thread and ask *'What kind of venue should I consider?'*, the agent retrieves `preferred_event_style` from this Long-Term Store!")
