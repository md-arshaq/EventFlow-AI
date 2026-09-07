"""
AI Event Planning & Coordination Assistant
Main Streamlit Application Entrypoint.
Demonstrating LangGraph StateGraph, Reducers, Context Trimming, and Dual-Memory Architecture.
"""
import streamlit as st
from dotenv import load_dotenv

# Load environment configuration (.env)
load_dotenv()

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Event Planning Assistant (LangGraph)",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import UI components
from ui.sidebar import render_sidebar
from ui.chat_view import render_chat_view
from ui.state_view import render_state_view
from ui.memory_view import render_memory_view
from ui.context_view import render_context_view
from ui.graph_view import render_graph_view
from ui.faculty_demo import render_faculty_demo


def main():
    # Render Sidebar
    render_sidebar()

    # Main Header
    st.title("🎪 AI Event Planning & Coordination Assistant")
    st.markdown(
        "**LangGraph Module 2 System** • *Typed State • Non-Default Reducers • Thread Checkpointing • Context Trimming • Long-Term Store*"
    )
    st.divider()

    # Navigation Tabs
    tab_chat, tab_state, tab_memory, tab_context, tab_graph, tab_demo = st.tabs([
        "💬 Chat",
        "📋 Event State & Reducers",
        "🧠 Memory (Short vs Long)",
        "📉 Context & Trimming",
        "🕸️ Graph Architecture",
        "🚀 5-Min Faculty Demo"
    ])

    with tab_chat:
        render_chat_view()

    with tab_state:
        render_state_view()

    with tab_memory:
        render_memory_view()

    with tab_context:
        render_context_view()

    with tab_graph:
        render_graph_view()

    with tab_demo:
        render_faculty_demo()


if __name__ == "__main__":
    main()
