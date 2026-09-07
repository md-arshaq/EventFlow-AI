import streamlit as st
from memory.long_term_store import get_long_term_store
from memory.threads_store import load_threads, add_or_update_thread


def render_sidebar():
    """Renders the Streamlit sidebar."""
    st.sidebar.title("🎪 Event Coordinator")
    st.sidebar.caption("LangGraph Module 2 Demonstration")
    st.sidebar.divider()

    # Thread Management Section with persistent storage
    st.sidebar.subheader("🧵 Conversations")

    threads = load_threads()
    st.session_state.threads = threads

    if "current_thread_id" not in st.session_state or st.session_state.current_thread_id not in threads:
        st.session_state.current_thread_id = list(threads.keys())[0]

    # Button to create new thread
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        new_thread_name = st.text_input("New Thread Name", placeholder="e.g., Tech Workshop", label_visibility="collapsed")
    with col2:
        if st.button("➕", help="Create new conversation thread"):
            if new_thread_name.strip():
                new_id = f"thread_{len(threads) + 1:03d}"
                add_or_update_thread(new_id, new_thread_name.strip())
                st.session_state.current_thread_id = new_id
                st.rerun()

    # Thread Selection
    thread_options = list(st.session_state.threads.keys())
    selected_thread = st.sidebar.radio(
        "Active Thread",
        thread_options,
        index=thread_options.index(st.session_state.current_thread_id) if st.session_state.current_thread_id in thread_options else 0,
        format_func=lambda tid: f"{st.session_state.threads[tid]} ({tid})",
        label_visibility="collapsed"
    )

    if selected_thread != st.session_state.current_thread_id:
        st.session_state.current_thread_id = selected_thread
        st.rerun()

    st.sidebar.divider()

    # Long-Term Profile Snapshot
    st.sidebar.subheader("👤 User Profile (Long-Term)")
    store = get_long_term_store()
    profile = store.get_profile("default_user")

    st.sidebar.markdown(f"**Name:** {profile.get('name', 'N/A')}")
    st.sidebar.markdown(f"**Preferred Style:** `{profile.get('preferred_event_style', 'N/A')}`")
    typical_b = profile.get('typical_budget')
    st.sidebar.markdown(f"**Typical Budget:** `₹{typical_b:,.0f}`" if typical_b else "**Typical Budget:** `N/A`")

    with st.sidebar.expander("✏️ Edit User Profile"):
        new_name = st.text_input("Name", value=profile.get("name", "Arshaq"))
        new_style = st.selectbox("Preferred Style", ["outdoor", "indoor", "rooftop", "banquet hall"], index=0)
        new_budget = st.number_input("Typical Budget (₹)", value=float(profile.get("typical_budget", 20000.0)), step=5000.0)
        if st.button("Save Profile Updates"):
            store.update_profile("default_user", {
                "name": new_name,
                "preferred_event_style": new_style,
                "typical_budget": new_budget
            })
            st.success("Profile saved!")
            st.rerun()

    st.sidebar.divider()

    # LLM Settings
    with st.sidebar.expander("⚙️ LLM & API Configuration", expanded=True):
        # Check Streamlit Cloud secrets, os.environ, or session state
        existing_key = (
            st.session_state.get("USER_GEMINI_KEY")
            or os.getenv("GEMINI_API_KEY")
            or (getattr(st, "secrets", {}).get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else "")
            or ""
        )

        api_key_input = st.text_input(
            "Gemini API Key",
            value=existing_key,
            type="password",
            help="Required on deployed versions. Get free key from aistudio.google.com/app/apikey"
        )
        if api_key_input and api_key_input.strip():
            st.session_state["USER_GEMINI_KEY"] = api_key_input.strip()
            os.environ["GEMINI_API_KEY"] = api_key_input.strip()

        model_choice = st.selectbox(
            "Model",
            [
                "gemini-3.1-flash-lite (500 req/day)",
                "gemini-3.5-flash-lite (500 req/day)",
                "gemini-3.6-flash (20 req/day)",
                "DemoChatModel (Offline & Unlimited)"
            ],
            index=0
        )
        clean_model = model_choice.split(" ")[0]
        st.session_state["SELECTED_MODEL"] = clean_model
        os.environ["GEMINI_MODEL"] = clean_model

        if "DemoChatModel" in model_choice:
            st.info("ℹ️ Using offline DemoChatModel.")
        elif not (os.getenv("GEMINI_API_KEY") or "").strip():
            st.warning("⚠️ No API Key found. Paste your Gemini API key above or add it to Streamlit Secrets to enable live AI responses.")
        else:
            st.success(f"✅ Live Gemini Model active: `{clean_model}`")
