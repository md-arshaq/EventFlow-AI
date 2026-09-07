"""
Graph Architecture Visualization Component.
Renders the compiled StateGraph structure using Mermaid diagram and ASCII representations.
"""
import streamlit as st
from graph.builder import get_graph_ascii, get_graph_mermaid


def render_graph_view():
    """Renders the LangGraph architecture visualization."""
    st.subheader("🕸️ Compiled LangGraph Architecture")
    st.caption("Visual representation of nodes, conditional routing, and state execution graph.")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### 🗺️ Graph Diagram (Mermaid)")
        mermaid_code = get_graph_mermaid()
        st.markdown(f"```mermaid\n{mermaid_code}\n```")

    with col2:
        st.markdown("### 🔠 ASCII Graph Output")
        ascii_code = get_graph_ascii()
        st.code(ascii_code, language="text")

    st.divider()

    st.markdown("### 📑 Graph Node & Conditional Routing Catalog")
    st.markdown("""
| Node Name | Node Type | Purpose / Action | State Reducers Used |
| :--- | :--- | :--- | :--- |
| **`router`** | Router Node | Classifies user intent (`event_info`, `tasks`, `guests`, `budget`, etc.) & updates Long-Term profile | Default |
| **`event_info_node`** | Processing Node | Extracts event type, guest count, date, location | Default |
| **`task_node`** | Processing Node | Extracts new tasks | **`operator.add`** (Non-default list reducer) |
| **`guest_node`** | Processing Node | Extracts guest names & attendees | **`operator.add`** (Non-default list reducer) |
| **`budget_node`** | Processing Node | Parses budget limit & creates allocations | Default |
| **`schedule_node`** | Processing Node | Generates timeline schedule | Default |
| **`memory_node`** | Processing Node | Handles long-term preference updates | Global Store |
| **`general_node`** | Processing Node | Handles brainstorming & open questions | Default |
| **`response_node`** | Unified Output | Performs Context Trimming, Token Metrics & LLM Invocation | **`add_messages`** (LangGraph message reducer) |
""")
