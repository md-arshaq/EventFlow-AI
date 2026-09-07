# AI Event Planning & Coordination Assistant

An educational conversational AI application demonstrating **LangGraph Module 2** core architecture:
1. **LangGraph StateGraph & Conditional Routing**
2. **State Management with Custom Reducers (`operator.add`)**
3. **Short-Term Memory (Thread-based Checkpointer) vs. Long-Term Memory (Global User Profile)**
4. **Message Trimming & Filtering with Live Token Metrics**

---

## 🏗️ Architecture & Component Overview

```
AAI_project/
├── app.py                      # Main Streamlit Application UI
├── requirements.txt            # Project Dependencies
├── .env.example                # Example Environment Variables (Gemini API Key)
├── README.md                   # System Architecture & Evaluation Guide
│
├── graph/
│   ├── state.py                # TypedDict EventState with non-default operator.add reducers
│   ├── router.py               # Intent classifier (event_info, tasks, guests, budget, schedule, memory)
│   ├── nodes.py                # Domain processing nodes & trimmed response generator
│   ├── conditional_edges.py    # Routing logic mapping intent to processing node
│   └── builder.py              # StateGraph assembly, compilation & visualization (ASCII/Mermaid)
│
├── memory/
│   ├── checkpointer.py         # Thread-based short-term memory checkpointer (MemorySaver)
│   └── long_term_store.py      # Cross-thread persistent user profile store (JSON backed)
│
├── utils/
│   ├── token_counter.py        # Token estimation engine
│   ├── filtering.py            # Intent-based message filtering
│   ├── trimming.py             # MAX_CONTEXT_TOKENS context window trimming
│   └── llm_factory.py          # Unified LLM provider (Google Gemini + offline DemoChatModel)
│
├── ui/
│   ├── sidebar.py              # Thread switching & profile editing
│   ├── chat_view.py            # Conversational chat interface
│   ├── state_view.py           # Structured event state & reducer accumulation display
│   ├── memory_view.py          # Short-Term vs. Long-Term dual-memory inspection
│   ├── context_view.py         # Live token reduction & message trimming charts
│   ├── graph_view.py           # Mermaid and ASCII graph architecture diagrams
│   └── faculty_demo.py         # 1-Click 7-Step faculty evaluation runner
│
└── tests/
    └── test_graph.py           # Automated test suite
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)
Copy `.env.example` to `.env` and add your free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey):
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
MAX_CONTEXT_TOKENS=1500
```
> *Note: If no API key is provided, the application seamlessly runs in offline mode using the smart built-in `DemoChatModel`.*

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Run Automated Tests
```bash
python tests/test_graph.py
```

---

## 🎓 5-Minute Faculty Evaluation Walkthrough

| Step | Goal | Action in UI | What is Demonstrated |
| :--- | :--- | :--- | :--- |
| **1. Graph** | Show Compiled Architecture | Open **🕸️ Graph Architecture** tab | `StateGraph`, `START -> router`, conditional edge to specialized nodes, converged to `response_node -> END`. |
| **2. State** | Initialize Event State | In **🚀 5-Min Faculty Demo**, click Step 2 (or send: *"I am planning a birthday party for 30 people on Dec 20"* in Chat) | Structured typed state fields (`event_type="Birthday Party"`, `guest_count=30`, `event_date="December 20"`). |
| **3. Reducer** | Test Non-Default Reducer | Click Step 3 in Demo tab to add *"Book venue"* and *"Order food"* | `operator.add` reducer appends new items to the task pipeline rather than overwriting existing items. |
| **4. Short-Term** | Test Thread Memory | Ask *"How many guests are attending?"* | LangGraph `MemorySaver` checkpointer recalls 30 guests from thread memory. |
| **5. Isolation** | Test Thread Separation | Click Step 5 to switch to `thread_002` (100 people) and alternate between threads | Switching threads isolates state (`thread_001` has 30 guests; `thread_002` has 100 guests). |
| **6. Long-Term** | Test Cross-Thread Store | Query *"What venue should I book?"* in `thread_002` | Agent recalls `preferred_event_style="outdoor"` saved in global user profile store. |
| **7. Trimming** | Test Token Management | Check **📉 Context & Trimming** tab after extended turns | Shows exact before/after message count and token reduction (e.g. 2,500 tokens → 950 tokens). |

---

## 🛡️ Core Concepts Implemented

1. **StateGraph**: Typed `EventState` utilizing LangGraph graph compilation.
2. **Conditional Edges**: Dynamic routing from `router` to domain nodes based on classified intent.
3. **Non-Default Reducers**: `tasks: Annotated[List[str], operator.add]` and `guest_list: Annotated[List[str], operator.add]`.
4. **Short-Term Memory**: `MemorySaver` checkpointer keyed by `thread_id`.
5. **Long-Term Memory**: Persistent store keyed by `user_id` surviving across threads and sessions.
6. **Context Trimming**: Filters and trims history to `MAX_CONTEXT_TOKENS` before model invocation while preserving full state in the checkpointer.
