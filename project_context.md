````markdown
# AI Event Planning & Coordination Assistant
## Complete Project Context & Implementation Specification

---

# 1. Project Overview

## Project Name

**AI Event Planning & Coordination Assistant**

## Project Type

LangGraph-based conversational AI application with a frontend.

## Primary Goal

Build a small but complete chat application that helps users plan and coordinate events such as:

- Birthday parties
- College events
- Workshops
- Meetups
- Seminars
- Small conferences
- Family gatherings
- Corporate/team events
- Social gatherings

The application must demonstrate the four concepts required in the LangGraph Module 2 assignment:

1. LangGraph Graph
2. State Management with Reducers
3. Message Trimming and Filtering
4. Short-Term and Long-Term Memory

The application should prioritize **clear demonstration of LangGraph mechanics** over sophisticated AI capabilities.

The LLM itself is not the primary focus. Any suitable LLM can be used, including:

- OpenAI
- Gemini
- Local LLM
- Offline DemoChatModel

The implementation must make it easy for a faculty member to visually verify that all four concepts are implemented correctly.

---

# 2. Core Problem Statement

Planning an event involves handling multiple pieces of information simultaneously:

- Event type
- Date
- Time
- Number of attendees
- Venue
- Budget
- Guest list
- Schedule
- Tasks
- Food requirements
- Equipment
- Preferences
- Previous planning decisions

Normal chatbots may simply maintain a conversation history, but this project demonstrates how LangGraph can be used to structure and manage this information.

The system should:

1. Understand the user's request.
2. Determine the intent of the request.
3. Route the request to the appropriate processing node.
4. Maintain conversation state.
5. Maintain structured event information.
6. Reduce unnecessary conversation history before calling the LLM.
7. Maintain short-term memory using a LangGraph checkpointer.
8. Maintain long-term user preferences using a persistent store.
9. Allow users to switch between independent conversation threads.
10. Demonstrate that long-term information survives thread changes.

---

# 3. Example User Scenario

A user creates a conversation called:

**Birthday Party**

They tell the assistant:

> I am planning a birthday party for 30 people on December 20.

Later:

> My preferred event style is outdoor and I usually keep the budget around ₹20,000.

The system stores these preferences in long-term memory.

The user then creates another thread:

**College Meetup**

They ask:

> Help me plan a college meetup.

The current conversation should NOT contain the birthday party conversation.

However, the assistant can retrieve the user's long-term preferences:

- Preferred style: outdoor
- Typical budget: ₹20,000

Therefore it can respond:

> You usually prefer outdoor events and a budget around ₹20,000. Would you like me to use those preferences for this meetup?

This demonstrates the difference between:

- Short-term memory
- Long-term memory
- Independent conversation threads

---

# 4. Application Scope

The application is NOT intended to be a production-grade event management platform.

It is an educational demonstration of LangGraph.

The system does NOT need to:

- Actually book venues
- Actually send invitations
- Process payments
- Integrate with Google Calendar
- Send emails
- Make real-world reservations
- Use complex multi-agent architecture
- Use a vector database
- Implement RAG

Keep the project small and focused on the LangGraph concepts being graded.

---

# 5. Main Application Features

The application must contain the following features.

## Feature 1: Chat Interface

Users should be able to:

- Enter a message
- Send the message
- Receive an AI response
- See conversation history
- Create a new conversation
- Switch between conversations

---

## Feature 2: Event Information Management

The system should maintain structured event information such as:

```text
event_type
event_name
event_date
event_time
location
guest_count
budget
guest_list
tasks
schedule
food_preferences
special_requirements
````

Not every field needs to be filled.

The state should be updated as the user provides information.

Example:

User:

> I'm planning a workshop for 50 people.

State:

```text
event_type = "Workshop"
guest_count = 50
```

Later:

> The budget is ₹30,000.

State becomes:

```text
event_type = "Workshop"
guest_count = 50
budget = 30000
```

---

# 6. LangGraph Architecture

The application must use a compiled LangGraph `StateGraph`.

The graph should contain:

* Typed State
* Multiple nodes
* Normal edges
* At least one conditional edge
* Checkpointer
* Long-term store integration

Recommended graph:

```text
                         START
                           |
                           v
                     +-------------+
                     |    Router   |
                     +-------------+
                       /    |    \
                      /     |     \
                     v      v      v
                Event Info Tasks  General
                   Node    Node   Chat Node
                     \      |      /
                      \     |     /
                       v    v    v
                    +-------------+
                    |  Response   |
                    +-------------+
                           |
                           v
                          END
```

---

# 7. Graph Nodes

At minimum, implement the following nodes.

## 7.1 Router Node

Purpose:

Determine what the user is asking about.

Possible intents:

```text
event_info
tasks
schedule
budget
guests
general
memory
```

The router should return the appropriate routing information.

Example:

```text
User:
"What should my event budget be?"

Router:
budget
```

Another example:

```text
User:
"Add Rahul and Ahmed to the guest list."

Router:
guests
```

The router does not necessarily need a separate LLM call.

It can use:

* Simple keyword-based routing
* LLM classification
* Hybrid logic

For this educational project, simple deterministic routing is acceptable.

---

# 8. Event Information Node

This node handles general event planning information.

Responsibilities:

* Understand event details
* Update event-related state
* Answer event planning questions
* Extract information from user messages

Examples:

```text
"I'm planning a birthday party."
```

Updates:

```text
event_type = "Birthday Party"
```

```text
"It will be for 40 people."
```

Updates:

```text
guest_count = 40
```

```text
"The event is on December 20."
```

Updates:

```text
event_date = "December 20"
```

---

# 9. Guest Management Node

Handles:

* Guest list
* Number of guests
* Adding guests
* Removing guests

Example:

```text
User:
Add Rahul and Ahmed to the guest list.
```

State:

```text
guest_list = [
    "Rahul",
    "Ahmed"
]
```

If the user later says:

```text
Add Priya.
```

The reducer should preserve existing values:

```text
guest_list = [
    "Rahul",
    "Ahmed",
    "Priya"
]
```

This provides a useful demonstration of a non-default reducer.

---

# 10. Task Management Node

Handles event tasks.

Example:

```text
User:
Add these tasks:
- Book venue
- Order food
- Send invitations
```

State:

```text
tasks = [
    "Book venue",
    "Order food",
    "Send invitations"
]
```

The tasks channel should use a non-default reducer such as:

```python
operator.add
```

This means new tasks are appended instead of replacing previous tasks.

---

# 11. Schedule Node

Handles event scheduling.

Example:

```text
User:
The event starts at 6 PM.
```

State:

```text
event_time = "6 PM"
```

It can also help construct a simple event schedule.

Example:

```text
6:00 PM - Guests arrive
6:30 PM - Main activity
7:30 PM - Food
8:30 PM - Closing
```

---

# 12. Budget Node

Handles event budget-related requests.

Example:

```text
User:
My total budget is ₹25,000.
```

State:

```text
budget = 25000
```

The assistant can optionally provide a simple breakdown:

```text
Venue: ₹8,000
Food: ₹10,000
Decoration: ₹4,000
Miscellaneous: ₹3,000
```

No actual financial transaction should occur.

---

# 13. General Chat Node

Handles requests that do not belong to a specific category.

Example:

```text
User:
Give me some ideas for a fun birthday party.
```

The general chat node should respond normally.

---

# 14. Response Node

A final response node may be used to:

* Generate the final response
* Summarize updated event state
* Format the answer
* Provide useful recommendations

If the specialized nodes themselves generate the final response, a separate response node is optional.

However, having a final response node makes the graph easier to demonstrate.

---

# 15. Conditional Edge

The graph MUST contain at least one conditional edge.

The router should determine the next node.

Conceptually:

```text
Router
   |
   +---- event_info ---> Event Node
   |
   +---- guests -------> Guest Node
   |
   +---- tasks --------> Task Node
   |
   +---- budget -------> Budget Node
   |
   +---- schedule -----> Schedule Node
   |
   +---- general ------> General Chat Node
```

This is important because the assignment explicitly requires a conditional edge.

---

# 16. Typed State

The application MUST use a typed LangGraph state.

Use an appropriate typing mechanism such as:

```text
TypedDict
```

The state should contain fields similar to:

```text
messages
event_type
event_name
event_date
event_time
location
guest_count
budget
guest_list
tasks
intent
```

Additional fields can be added if useful.

---

# 17. State Management

The application must demonstrate that state is not simply a collection of variables.

LangGraph should manage the state throughout the graph execution.

Example:

```text
User message
      |
      v
   Router
      |
      v
 Event Node
      |
      v
 State Updated
```

The updated state should remain available to later nodes.

---

# 18. Reducers

The assignment specifically requires:

> At least one channel with a non-default reducer.

The application should use:

## Messages

Use:

```text
add_messages
```

for the messages channel.

This is the standard LangGraph message reducer.

---

## Tasks

Use a non-default reducer for tasks.

Recommended:

```text
operator.add
```

Conceptually:

```text
Existing tasks:
[
    "Book venue"
]

New tasks:
[
    "Order food"
]

After reducer:
[
    "Book venue",
    "Order food"
]
```

This demonstrates that the reducer combines new information with existing state rather than replacing it.

---

# 19. Optional Additional Reducer

The guest list can also use an append-style reducer.

Example:

```text
Existing:
["Rahul"]

New:
["Ahmed", "Priya"]

Result:
["Rahul", "Ahmed", "Priya"]
```

This is optional but provides a stronger demonstration.

---

# 20. Checkpointer

The application MUST use a LangGraph checkpointer.

The purpose is to provide short-term conversational memory.

The checkpointer should save graph state for a particular thread.

Possible implementations:

* In-memory checkpointer for a simple demo
* SQLite checkpointer for persistence
* Another supported LangGraph checkpointer

For the assignment, an in-memory solution is acceptable if the demonstration only needs to occur while the application is running.

SQLite is preferable if practical because it makes persistence easier to demonstrate.

---

# 21. Thread IDs

Every conversation must have a unique `thread_id`.

Example:

```text
thread_001
thread_002
thread_003
```

The frontend should allow the user to switch between them.

Example UI:

```text
CONVERSATIONS

+ Create New

• Birthday Party
• College Workshop
• Family Gathering
```

Each conversation should map to a separate thread ID.

---

# 22. Thread Isolation

This is an important demonstration.

Thread 1:

```text
Name: Birthday Party
Guests: 30
Budget: ₹20,000
```

Thread 2:

```text
Name: College Workshop
Guests: 50
Budget: ₹30,000
```

When the user switches from Thread 1 to Thread 2:

Thread 2 must NOT automatically contain Thread 1's short-term conversation history.

The checkpointer must maintain separate state for each thread.

---

# 23. Short-Term Memory

Short-term memory is implemented using the LangGraph checkpointer.

It should preserve:

* Conversation messages
* Current event state
* Current thread context
* Tasks
* Guest list
* Other temporary state

Example:

Thread 1:

```text
User:
The party is for 30 people.

AI:
Got it.
```

Later:

```text
User:
What is the guest count?
```

AI:

```text
The event currently has 30 guests.
```

This proves short-term memory.

---

# 24. Long-Term Memory

The application must also implement a long-term memory store.

The store must work independently from the conversation thread.

This means:

```text
Thread 1
    |
    v
Long-Term Store
    |
    +------------------+
                       |
Thread 2               |
    |                  |
    +----> Retrieve <---+
```

The long-term store should contain a small user profile.

Recommended profile:

```text
name
preferred_event_style
typical_budget
```

At minimum:

```text
name
one preference
```

---

# 25. Long-Term Memory Example

Thread 1:

User:

```text
My name is Arshaq and I prefer outdoor events.
```

The application should save:

```text
Profile:
{
    name: "Arshaq",
    preferred_event_style: "outdoor"
}
```

Then the user creates Thread 2.

User:

```text
Help me plan an event.
```

The system retrieves:

```text
preferred_event_style = outdoor
```

The assistant can respond:

```text
Since you prefer outdoor events, we can prioritize an outdoor venue.
```

This proves that long-term memory survives across threads.

---

# 26. Long-Term Memory vs Short-Term Memory

The UI should make the difference clear.

Example:

```text
MEMORY

Short-Term Memory
Current Thread:
Birthday Party
Messages:
12

Long-Term Memory
Name:
Arshaq

Preferred Event Style:
Outdoor
```

When switching threads:

```text
Current Thread:
College Meetup

Short-Term Memory:
New conversation

Long-Term Memory:
Name: Arshaq
Preference: Outdoor
```

This provides a very clear demonstration.

---

# 27. Message Trimming

The application MUST trim conversation history before every model call.

The purpose is to avoid sending unnecessary historical messages to the LLM.

Example:

```text
Full history:

30 messages
      |
      v
Trim / Filter
      |
      v
10 messages
      |
      v
LLM
```

The actual LangGraph state may still contain the full conversation history.

Only the messages supplied to the model should be trimmed.

---

# 28. Token Budget

Define a token budget for model context.

Example:

```text
MAX_CONTEXT_TOKENS = 1500
```

Before every model call:

1. Retrieve current messages.
2. Filter irrelevant messages if applicable.
3. Trim them to the token budget.
4. Send only the resulting messages to the model.

Do NOT delete the original messages from the checkpointer simply because they were trimmed for the model call.

---

# 29. Filtering

In addition to trimming, the system may filter messages.

Example:

If the user is asking about budget:

```text
Relevant:
- Budget discussion
- Event size
- Guest count
- Venue cost

Potentially irrelevant:
- Previous general greetings
- Unrelated conversation
```

The model should receive only the useful context.

Filtering can be implemented using:

* Intent-based filtering
* Message type filtering
* Keyword filtering
* Simple relevance logic

Keep it understandable rather than overly complicated.

---

# 30. Demonstrating Trimming in UI

The UI MUST visibly show the effect.

Create a section such as:

```text
CONTEXT MANAGEMENT

Messages in history:     24
Messages sent to model:  8

Tokens before trimming:  3100
Tokens after trimming:   1200
```

This is important because the assignment explicitly requires the effect to be visible.

The application should update these values after each model call.

---

# 31. Model Context Flow

The model call should conceptually work like:

```text
State messages
      |
      v
Filter messages
      |
      v
Trim to token budget
      |
      v
Messages sent to LLM
      |
      v
LLM response
```

The original state remains intact.

---

# 32. Frontend Requirements

The frontend should be simple but demonstrate all important features.

Recommended layout:

```text
+-------------------------------------------------------------+
|          AI EVENT PLANNING & COORDINATION ASSISTANT         |
+----------------------+--------------------------------------+
|                      |                                      |
|   CONVERSATIONS      |              CHAT                    |
|                      |                                      |
|   + New Thread       |   User: I'm planning a birthday      |
|                      |   party for 30 people.                |
|   Birthday Party     |                                      |
|   College Meetup     |   AI: Great! Let's plan it.           |
|   Workshop           |                                      |
|                      |                                      |
|                      |                                      |
|                      |                                      |
+----------------------+--------------------------------------+
| CONTEXT MANAGEMENT | MEMORY | EVENT STATE | GRAPH         |
+-------------------------------------------------------------+
```

---

# 33. Sidebar

The sidebar should contain:

```text
CONVERSATIONS

[ + New Conversation ]

Birthday Party
College Meetup
College Workshop
Family Event
```

Clicking a conversation should switch its `thread_id`.

---

# 34. Chat Area

The chat area should show:

* User messages
* Assistant messages
* Current conversation

Example:

```text
You:
I'm planning a birthday party for 30 people.

Assistant:
Great! What date are you considering?
```

---

# 35. Event State Panel

Show structured state.

Example:

```text
EVENT STATE

Event Type:
Birthday Party

Date:
December 20

Time:
6:00 PM

Guests:
30

Budget:
₹20,000

Location:
Not specified
```

This makes state management visible.

---

# 36. Task Panel

Show current tasks.

Example:

```text
EVENT TASKS

✓ Choose event date
□ Book venue
□ Order food
□ Send invitations
□ Arrange decorations
```

The task list should be backed by the reducer-managed state.

---

# 37. Memory Panel

Show both memory types.

Example:

```text
MEMORY

SHORT-TERM
Thread:
Birthday Party

Messages:
14

LONG-TERM
Name:
Arshaq

Preferred Style:
Outdoor

Typical Budget:
₹20,000
```

---

# 38. Context Panel

Show trimming/filtering.

Example:

```text
MODEL CONTEXT

Before:
24 messages
3,200 tokens

After filtering/trimming:
8 messages
1,150 tokens

Messages sent to model:
8
```

This is one of the most important UI elements.

---

# 39. Graph Visualization Panel

The application MUST display the LangGraph graph somewhere in the UI.

Use one of:

```text
draw_ascii()
```

or

```text
draw_mermaid_png()
```

The easiest implementation is `draw_ascii()`.

Example:

```text
          START
            |
          Router
        /   |   \
       /    |    \
   Event  Tasks  General
       \    |    /
          Response
             |
            END
```

If using `draw_mermaid_png()`, render the resulting graph image in the frontend.

---

# 40. Recommended UI Tabs

A clean implementation can use tabs:

```text
[ Chat ] [ Event State ] [ Memory ] [ Graph ] [ Debug ]
```

### Chat

Normal conversation.

### Event State

Display structured state.

### Memory

Display short-term and long-term memory.

### Graph

Display the LangGraph visualization.

### Debug

Display:

* Intent
* Message count
* Token count
* Trimmed message count
* Current thread ID
* Current state information

---

# 41. Debug Information

The application should expose useful information for demonstration.

Example:

```text
DEBUG

Thread ID:
thread_001

Detected Intent:
event_info

Messages in State:
18

Messages Sent to Model:
7

Tokens Before:
2800

Tokens After:
1100

Long-Term Memory:
Loaded

Checkpointer:
Active
```

This makes it extremely easy for a faculty member to verify the implementation.

---

# 42. Suggested Technology Stack

## Backend

Python

## Framework

LangGraph

## LLM

Any supported model.

Possible options:

* OpenAI
* Gemini
* Local model
* DemoChatModel

Choose the simplest model available.

## Frontend

Recommended:

```text
Streamlit
```

because the project is primarily a demonstration and Streamlit makes it easy to build:

* Chat interface
* Sidebar
* Tabs
* Buttons
* State displays
* Graph visualization
* Debug panels

Alternative:

```text
React + FastAPI
```

but this is unnecessary for a small academic demonstration.

---

# 43. Suggested Project Structure

Use a clean structure similar to:

```text
event-planner-langgraph/
│
├── app.py
│
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── nodes.py
│   ├── router.py
│   └── graph.py
│
├── memory/
│   ├── checkpointer.py
│   └── long_term.py
│
├── utils/
│   ├── trimming.py
│   ├── filtering.py
│   └── token_counter.py
│
├── ui/
│   ├── chat.py
│   ├── sidebar.py
│   └── panels.py
│
├── requirements.txt
├── README.md
└── .env
```

The exact structure can be simplified if needed.

---

# 44. Graph State Design

A conceptual state schema:

```text
State
│
├── messages
│
├── intent
│
├── event_type
│
├── event_name
│
├── event_date
│
├── event_time
│
├── location
│
├── guest_count
│
├── budget
│
├── guest_list
│
├── tasks
│
└── context_metadata
```

Where:

```text
messages
```

uses:

```text
add_messages
```

and:

```text
tasks
```

uses:

```text
operator.add
```

or another clearly defined non-default reducer.

---

# 45. Example Conversation

## Thread 1 — Birthday Party

User:

```text
I'm planning a birthday party.
```

Router:

```text
event_info
```

State:

```text
event_type = birthday party
```

Assistant:

```text
Great! How many people are you expecting?
```

---

User:

```text
Around 30 people.
```

State:

```text
guest_count = 30
```

---

User:

```text
My budget is ₹20,000.
```

State:

```text
budget = 20000
```

---

User:

```text
I prefer outdoor events.
```

Long-term memory:

```text
preferred_event_style = outdoor
```

---

User:

```text
Add booking the venue to my tasks.
```

Tasks:

```text
[
    "Book venue"
]
```

---

User:

```text
Also add sending invitations.
```

Reducer:

```text
[
    "Book venue",
    "Send invitations"
]
```

This demonstrates the reducer.

---

# 46. New Thread Demonstration

Create:

```text
Thread 2
```

Name:

```text
College Meetup
```

User:

```text
Help me plan a college meetup.
```

Thread 2 starts with its own short-term conversation.

However, long-term memory retrieves:

```text
preferred_event_style = outdoor
```

Assistant:

```text
You previously indicated that you prefer outdoor events. Would you like to prioritize an outdoor venue for this meetup?
```

This demonstrates long-term memory across threads.

---

# 47. Thread Isolation Demonstration

Thread 1:

```text
Birthday Party
Guests = 30
Budget = ₹20,000
```

Thread 2:

```text
College Meetup
Guests = 100
Budget = ₹50,000
```

Switch back to Thread 1.

The state should still be:

```text
Guests = 30
Budget = ₹20,000
```

Switch to Thread 2.

The state should be:

```text
Guests = 100
Budget = ₹50,000
```

This proves the checkpointer and thread IDs work correctly.

---

# 48. Trimming Demonstration

Create enough conversation history.

For example:

```text
Messages in state:
20
```

Set:

```text
MAX_CONTEXT_TOKENS = 1000
```

Before the model call:

```text
20 messages
2500 tokens
```

After trimming:

```text
7 messages
950 tokens
```

Send only the 7 messages to the LLM.

The UI should show:

```text
2500 tokens → 950 tokens
20 messages → 7 messages
```

---

# 49. Important Design Rule for Trimming

Do NOT confuse:

```text
State history
```

with:

```text
Model context
```

The checkpointer can retain the complete conversation.

The trimming function should only determine what gets passed into the next model call.

Conceptually:

```text
             Checkpointer
                  |
                  v
        Complete Conversation
                  |
          +-------+-------+
          |               |
          v               v
      UI History      Trim/Filter
                          |
                          v
                     Model Context
                          |
                          v
                         LLM
```

---

# 50. Long-Term Store Design

Use a small profile schema.

Example:

```text
UserProfile

{
    "name": "...",
    "preferred_event_style": "...",
    "typical_budget": "..."
}
```

The store should use a stable user identifier.

The key should NOT be the thread ID.

This is important because long-term memory must survive across threads.

Conceptually:

```text
User ID
   |
   +--------------------+
   |                    |
Thread 1             Thread 2
   |                    |
   +---------+----------+
             |
       Long-Term Profile
```

---

# 51. Memory Update Logic

When the user provides a stable preference:

```text
"My preferred event style is outdoor."
```

Extract:

```text
preferred_event_style = outdoor
```

Save it to long-term memory.

When a new thread begins:

```text
Load user profile
```

Retrieve:

```text
preferred_event_style
```

Make it available to the graph.

---

# 52. Avoid Unnecessary Memory

Do not save every message to long-term memory.

Only save stable information such as:

* Name
* Preferred event style
* Typical budget
* Preferred event size
* General planning preferences

Do NOT save temporary information such as:

* Current question
* Current response
* Temporary task
* Current thread's entire conversation

Those belong to short-term state.

---

# 53. Error Handling

The application should gracefully handle:

* Empty messages
* Invalid input
* Missing LLM API key
* Model failure
* Invalid thread ID
* Empty event state
* Token counting failure

The application should not crash when the user sends an empty message.

---

# 54. API Key Handling

If an external LLM is used:

Use environment variables.

Example:

```text
OPENAI_API_KEY
```

or:

```text
GOOGLE_API_KEY
```

Do NOT hardcode API keys in source code.

Use:

```text
.env
```

for local development.

---

# 55. Requirements File

The project should have a `requirements.txt`.

It should contain only the packages actually required by the implementation.

Potential dependencies:

```text
langgraph
langchain
streamlit
python-dotenv
```

Additional packages can be included if required by the selected model or tokenization method.

---

# 56. UI Demonstration Requirements

The final application MUST visibly demonstrate all four topics.

## Topic 1 — Graph

Show:

```text
Graph Visualization
```

with nodes and conditional routing.

---

## Topic 2 — State + Reducers

Show:

```text
Current State
Tasks
Guest List
Messages
Thread ID
```

Demonstrate tasks being appended rather than overwritten.

---

## Topic 3 — Trimming + Filtering

Show:

```text
Before:
X messages
Y tokens

After:
A messages
B tokens
```

---

## Topic 4 — Memory

Show:

```text
Short-Term Memory
Long-Term Memory
```

Then demonstrate long-term memory in a new thread.

---

# 57. Faculty Demo Flow

The application should be designed so that the complete demonstration can be done in approximately 5–10 minutes.

Recommended demo:

## Step 1 — Show Graph

Open the Graph tab.

Explain:

```text
This is my compiled LangGraph StateGraph.
The router uses a conditional edge to determine which node handles the request.
```

---

## Step 2 — Demonstrate State

Create Thread 1.

Say:

```text
I'm planning a birthday party for 30 people.
```

Show Event State:

```text
Event Type:
Birthday Party

Guests:
30
```

---

## Step 3 — Demonstrate Reducer

Say:

```text
Add "Book venue" to my tasks.
```

Then:

```text
Add "Order food" to my tasks.
```

Show:

```text
Tasks:
Book venue
Order food
```

Explain:

```text
The tasks channel uses a non-default reducer that appends new tasks rather than replacing the existing list.
```

---

## Step 4 — Demonstrate Short-Term Memory

Ask:

```text
How many guests are attending?
```

Assistant:

```text
30 guests.
```

Explain:

```text
The checkpointer maintains the state for this thread.
```

---

## Step 5 — Demonstrate Thread Separation

Create Thread 2.

Say:

```text
I'm planning a college meetup for 100 people.
```

Then switch between Thread 1 and Thread 2.

Show:

```text
Thread 1 → 30 guests
Thread 2 → 100 guests
```

Explain:

```text
Each thread has independent short-term state.
```

---

## Step 6 — Demonstrate Long-Term Memory

In Thread 1 say:

```text
I prefer outdoor events.
```

Store it in long-term memory.

Create Thread 2.

Ask:

```text
What kind of venue should I consider?
```

Assistant should use the stored preference.

Explain:

```text
The preference was retrieved from the long-term store rather than the current thread's conversation history.
```

---

## Step 7 — Demonstrate Trimming

Have enough conversation history.

Show the Context panel:

```text
Before:
20 messages
2500 tokens

After:
7 messages
950 tokens
```

Explain:

```text
The complete history remains in state, but only the trimmed context is passed to the model.
```

---

# 58. What Must NOT Be Overengineered

Do not add unnecessary complexity.

Avoid:

* Multi-agent systems
* RAG
* Vector databases
* Complex authentication
* Payment integration
* Real venue APIs
* Real booking systems
* Complex frontend frameworks unless necessary
* Excessive LLM calls
* Complicated database architecture

The purpose is to demonstrate LangGraph fundamentals.

---

# 59. Primary Evaluation Criteria

The implementation should optimize for these criteria:

### 1. Correct LangGraph Architecture

The graph must actually be implemented using LangGraph.

### 2. Typed State

Use a clearly defined typed state.

### 3. Multiple Nodes

Have at least two meaningful nodes.

### 4. Conditional Edge

The router must conditionally select a node.

### 5. Reducer

Use:

```text
add_messages
```

plus at least one additional non-default reducer.

### 6. Checkpointer

Use a real LangGraph checkpointer with thread IDs.

### 7. Thread Switching

The frontend must allow switching between conversations.

### 8. Trimming / Filtering

The model must receive trimmed/filtered messages.

### 9. Visible Trimming Metrics

The UI must display the effect.

### 10. Short-Term Memory

Demonstrate state persistence within a thread.

### 11. Long-Term Memory

Demonstrate profile persistence across threads.

### 12. Clear UI

All four topics must be easy to demonstrate.

---

# 60. Recommended Final Architecture

The complete architecture should look approximately like:

```text
                         FRONTEND
                        Streamlit UI
                             |
                +------------+-------------+
                |            |             |
            Chat UI      Thread UI      Debug UI
                |            |             |
                +------------+-------------+
                             |
                             v
                     LANGGRAPH ENGINE
                             |
                             v
                    +----------------+
                    | Typed Graph    |
                    | State          |
                    +----------------+
                             |
                             v
                         Router
                             |
            +----------------+----------------+
            |                |                |
            v                v                v
       Event Node       Task Node       General Node
            |                |                |
            +----------------+----------------+
                             |
                             v
                      Context Manager
                             |
                    +--------+--------+
                    |                 |
                    v                 v
                Filtering          Trimming
                    |                 |
                    +--------+--------+
                             |
                             v
                            LLM
                             |
                             v
                         Response
                             |
                             v
                      Checkpointer
                             |
                             v
                       Thread State


                    LONG-TERM MEMORY
                           |
                           v
                    User Profile Store
                           |
             +-------------+-------------+
             |                           |
          Thread 1                    Thread 2
             |                           |
             +-------------+-------------+
                           |
                     Same User Profile
```

---

# 61. Final User Experience

When the user opens the application, they should see:

```text
============================================================
       AI EVENT PLANNING & COORDINATION ASSISTANT
============================================================

Sidebar:
------------------------------------------------------------
CONVERSATIONS

+ New Conversation

Birthday Party
College Meetup
Workshop
------------------------------------------------------------

Main:
------------------------------------------------------------
CHAT

User:
I'm planning a birthday party for 30 people.

Assistant:
Great! Let's start planning your event.

------------------------------------------------------------

EVENT STATE

Type: Birthday Party
Guests: 30
Date: Not specified
Time: Not specified
Budget: Not specified

------------------------------------------------------------

CONTEXT MANAGEMENT

Messages before: 12
Messages sent to model: 6

Tokens before: 2100
Tokens after: 950

------------------------------------------------------------

MEMORY

Short-term:
Current Thread = Birthday Party

Long-term:
Name = Arshaq
Preferred Style = Outdoor

------------------------------------------------------------

LANGGRAPH

START
  |
Router
 / | \
Event Tasks General
 \ | /
Response
  |
 END
============================================================
```

---

# 62. Definition of Done

The project is considered complete only when ALL of the following are true:

* [ ] A working frontend exists.
* [ ] The frontend supports chat.
* [ ] The application uses LangGraph.
* [ ] A compiled StateGraph exists.
* [ ] The graph has a typed State.
* [ ] The graph has at least two nodes.
* [ ] The graph has at least one conditional edge.
* [ ] The graph visualization is displayed in the UI.
* [ ] `messages` uses `add_messages`.
* [ ] At least one additional channel uses a non-default reducer.
* [ ] A checkpointer is configured.
* [ ] Thread IDs are used.
* [ ] The user can create multiple threads.
* [ ] The user can switch between threads.
* [ ] Thread state remains isolated.
* [ ] Message history is trimmed and/or filtered before model calls.
* [ ] The original conversation state remains available.
* [ ] The UI displays before/after message counts or token counts.
* [ ] Short-term memory works using the checkpointer.
* [ ] A long-term store is implemented.
* [ ] A user profile is stored.
* [ ] Long-term memory survives across threads.
* [ ] The UI visibly demonstrates long-term memory.
* [ ] The application handles errors gracefully.
* [ ] API keys are not hardcoded.
* [ ] A README explains the architecture.
* [ ] The project can be demonstrated easily in 5–10 minutes.

---

# 63. Important Implementation Philosophy

The project should be built for **demonstrability**.

Every assignment requirement should have:

1. An implementation in the backend.
2. A visible representation in the frontend.
3. A simple demonstration scenario.

The faculty member should not need to inspect every line of code to understand the four concepts.

The UI should make the following immediately obvious:

```text
GRAPH
    ↓
STATE
    ↓
REDUCERS
    ↓
THREADS / CHECKPOINTER
    ↓
TRIMMING / FILTERING
    ↓
SHORT-TERM MEMORY
    ↓
LONG-TERM MEMORY
```

The implementation should favor **simple, reliable, understandable code** over unnecessary sophistication.

---

# 64. Final Objective

Build a polished educational LangGraph application called:

**AI Event Planning & Coordination Assistant**

The application should demonstrate how a conversational AI system can:

* Route requests through a graph
* Maintain structured state
* Combine state using reducers
* Persist conversations using thread-based checkpoints
* Keep different conversations isolated
* Trim and filter model context
* Maintain short-term conversational memory
* Maintain long-term user preferences
* Recall those preferences across independent threads
* Visually expose all of these mechanics through a simple frontend

The project should be small enough to implement and understand completely, while being sufficiently complete to satisfy every requirement of the LangGraph Module 2 assignment.

```
```
