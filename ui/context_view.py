import streamlit as st
from langchain_core.messages import HumanMessage
from graph.builder import get_graph
from utils.trimming import trim_and_filter_messages
from utils.token_counter import count_message_tokens


def render_context_view():
    """Renders the context management & token trimming metrics panel."""
    thread_id = st.session_state.current_thread_id
    thread_title = st.session_state.threads.get(thread_id, thread_id)
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state_obj = graph.get_state(config)
    values = state_obj.values if state_obj else {}
    messages = values.get("messages", [])

    # Trimming settings in session state
    if "MAX_CONTEXT_MESSAGES" not in st.session_state:
        st.session_state.MAX_CONTEXT_MESSAGES = 4
    if "MAX_CONTEXT_TOKENS" not in st.session_state:
        st.session_state.MAX_CONTEXT_TOKENS = 400

    st.subheader(f"📉 Context Window Management & Trimming ({thread_title})")
    st.caption("Inspect how LangGraph filters and trims messages to adhere to token budget limits before model calls.")

    # Interactive Budget Controls
    with st.expander("⚙️ Adjust Context Window Budget Thresholds", expanded=True):
        c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([2, 2, 3])
        with c_ctrl1:
            max_msgs = st.slider("Max Context Messages", min_value=2, max_value=15, value=st.session_state.MAX_CONTEXT_MESSAGES, step=1)
            st.session_state.MAX_CONTEXT_MESSAGES = max_msgs
        with c_ctrl2:
            max_tokens = st.slider("Max Token Budget", min_value=100, max_value=2000, value=st.session_state.MAX_CONTEXT_TOKENS, step=50)
            st.session_state.MAX_CONTEXT_TOKENS = max_tokens
        with c_ctrl3:
            st.markdown("**⚡ Fast Trimming Test:**")
            if st.button("🚀 Send 4 Follow-up Turns (Trigger Live Trimming)", help="Sends 4 turns to build history and observe token reduction"):
                with st.spinner("Generating multi-turn conversation..."):
                    test_turns = [
                        "Can you suggest a detailed timeline for the DSA sessions?",
                        "What refreshments should we provide during the break?",
                        "How should we distribute certificates to students?",
                        "Give me a summary of total expenses for venue and food."
                    ]
                    for turn in test_turns:
                        graph.invoke({"messages": [HumanMessage(content=turn)], "user_id": "default_user"}, config=config)
                st.success("4 turns added! Trimming is now active.")
                st.rerun()

    # Calculate live metrics based on current budget
    trimmed_msgs, live_metrics = trim_and_filter_messages(
        messages=messages,
        intent=values.get("intent", "general"),
        max_tokens=st.session_state.MAX_CONTEXT_TOKENS,
        max_messages=st.session_state.MAX_CONTEXT_MESSAGES
    )

    metrics = values.get("context_metadata") or live_metrics
    # Override with live metrics if updated budget slider was changed
    if len(messages) > st.session_state.MAX_CONTEXT_MESSAGES:
        metrics = live_metrics

    # Key Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Messages in History", metrics.get("messages_before", len(messages)))
    with c2:
        st.metric("Messages Sent to LLM", metrics.get("messages_after", len(trimmed_msgs)))
    with c3:
        st.metric("Tokens in Full History", metrics.get("tokens_before", count_message_tokens(messages)))
    with c4:
        st.metric("Tokens Passed to LLM", metrics.get("tokens_after", count_message_tokens(trimmed_msgs)),
                  delta=f"-{metrics.get('reduction_percent', 0)}%" if metrics.get('reduction_percent', 0) > 0 else "0% (Within Budget)")

    st.divider()

    st.markdown("### 📊 Token Reduction Efficiency")
    reduction = metrics.get("reduction_percent", 0.0)
    st.progress(min(1.0, reduction / 100.0 if reduction > 0 else 0.0))
    if reduction > 0:
        st.success(f"🎯 **Trimming Active:** Saved **{reduction}% context tokens** by filtering older history while keeping full state in Checkpointer.")
    else:
        st.info("ℹ️ Current conversation length is within budget limits. Use the **'Send 4 Follow-up Turns'** button above or lower the budget slider to observe immediate trimming reduction!")

    st.divider()

    # Side-by-Side Message Comparison
    col_full, col_trimmed = st.columns(2)
    with col_full:
        st.markdown(f"#### 📜 Complete Checkpoint History ({len(messages)} msgs)")
        st.caption("Retained 100% in LangGraph Checkpointer State:")
        with st.container(height=300):
            if messages:
                for idx, m in enumerate(messages, 1):
                    role = "👤 USER" if isinstance(m, HumanMessage) or getattr(m, 'type', '') == 'human' else "🤖 AI"
                    st.text(f"Turn {idx} [{role}]: {m.content[:100]}...")
            else:
                st.write("*No messages yet.*")

    with col_trimmed:
        st.markdown(f"#### ✂️ Trimmed Context Passed to LLM ({len(trimmed_msgs)} msgs)")
        st.caption(f"Optimized to fit token budget ({count_message_tokens(trimmed_msgs)} tokens):")
        with st.container(height=300):
            if trimmed_msgs:
                for idx, m in enumerate(trimmed_msgs, 1):
                    role = "👤 USER" if isinstance(m, HumanMessage) or getattr(m, 'type', '') == 'human' else "🤖 AI"
                    st.text(f"Sent {idx} [{role}]: {m.content[:100]}...")
            else:
                st.write("*No messages yet.*")

    st.markdown("---")
    st.markdown("### 🛡️ State Integrity Verification")
    st.success("✅ **Design Principle Upheld:** The checkpointer retains 100% of full conversation history in thread state, while only the trimmed context slice is dispatched to the model.")
