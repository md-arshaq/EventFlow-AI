"""
State and Reducers Visualization Component.
Demonstrates structured event attributes and highlights non-default 'operator.add' reducer accumulation.
"""
import streamlit as st
from graph.builder import get_graph


def render_state_view():
    """Renders structured event state and task reducer inspection."""
    thread_id = st.session_state.current_thread_id
    thread_title = st.session_state.threads.get(thread_id, thread_id)
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state_obj = graph.get_state(config)
    values = state_obj.values if state_obj else {}

    st.subheader(f"📋 Structured Event State ({thread_title})")
    st.caption("Inspect live variables updated by LangGraph nodes and managed via State Reducers.")

    # Top Metrics Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Event Type", values.get("event_type") or "Not set")
    with c2:
        count = values.get("guest_count")
        st.metric("Guest Count", f"{count} attendees" if count else "Not set")
    with c3:
        b = values.get("budget")
        st.metric("Budget", f"₹{b:,.0f}" if b else "Not set")
    with c4:
        st.metric("Event Date", values.get("event_date") or "Not set")

    st.divider()

    # Reducer Demonstration: Tasks and Guests
    col_tasks, col_guests = st.columns(2)

    with col_tasks:
        st.markdown("### 📝 Tasks Pipeline (`operator.add` Reducer)")
        st.info("💡 **Reducer Mechanics:** When new tasks are returned, `operator.add` appends them to this list instead of replacing previous items.")
        tasks = values.get("tasks", [])
        if tasks:
            for idx, task in enumerate(tasks, 1):
                st.checkbox(f"{task}", value=False, key=f"task_{thread_id}_{idx}")
        else:
            st.markdown("*No tasks added yet. Try: 'Add Book venue to my tasks'*")

    with col_guests:
        st.markdown("### 👥 Guest List (`operator.add` Reducer)")
        st.info("💡 **Reducer Mechanics:** New guest names accumulate incrementally across conversation turns.")
        guests = values.get("guest_list", [])
        if guests:
            for g in guests:
                st.markdown(f"- 👤 **{g}**")
        else:
            st.markdown("*No individual guests registered yet. Try: 'Add Rahul and Ahmed to guest list'*")

    st.divider()

    # Schedule & Location Section
    col_sched, col_loc = st.columns(2)
    with col_sched:
        st.markdown("### ⏰ Schedule Timeline")
        sched = values.get("schedule", [])
        if sched:
            for item in sched:
                st.markdown(f"• {item}")
        else:
            st.markdown(f"Start Time: `{values.get('event_time', 'Not specified')}`")

    with col_loc:
        st.markdown("### 📍 Location & Intent")
        st.markdown(f"**Venue:** `{values.get('location', 'Not specified')}`")
        st.markdown(f"**Last Classified Intent:** `{values.get('intent', 'None')}`")
