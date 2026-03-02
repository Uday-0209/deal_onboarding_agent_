from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
#from v1.Backend.graph import chat_node
from v1.Backend.llm_client import extract_intake_fields, make_conversational, generate_deal_title_from_intake

# -----------------------------
# Intake configuration
# -----------------------------

MANDATORY_FIELDS = ["deal_type", "deal_size", "geography"]

INTAKE_QUESTIONS = {
    "deal_type": "What type of deal is this? (e.g. debt, equity, project finance)",
    "deal_size": "What is the approximate deal size?",
    "geography": "Which geography or country does this deal relate to?",
    "sector": "What sector or asset class is this deal in?"
}

# -----------------------------
# LangGraph State
# -----------------------------

class ScoutState(TypedDict):
    messages: List[dict]
    phase: str
    deal_title: Optional[str]
    intake: Dict[str, Optional[str]]
    current_question: Optional[str]
    intro_done: bool
    intake_confirmed: bool

CONFIRMATION_KEYWORDS = [
    "yes",
    "proceed",
    "let's start",
    "ready",
    "continue"
]


def user_confirmed_intake(message: str) -> bool:
    msg = message.lower()
    return any(word in msg for word in CONFIRMATION_KEYWORDS)
# -----------------------------
# Nodes
# -----------------------------

# def extract_intake_node(state: ScoutState) -> ScoutState:
#     last_user_msg = next(
#         (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"),
#         None
#     )

#     if not last_user_msg:
#         return state

#     extracted = extract_intake_fields(last_user_msg)

#     for field, value in extracted.items():
#         if field in state["intake"] and state["intake"][field] is None:
#             state["intake"][field] = value

#     return state
def extract_intake_node(state: ScoutState) -> ScoutState:
    
    last_user_message = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"),
        None
    )

    if not last_user_message:
        return state

    # ✅ If we explicitly asked a question, trust the reply
    if state.get("current_question"):
        field = state["current_question"]
        if state["intake"].get(field) is None:
            state["intake"][field] = last_user_message.strip()
        state["current_question"] = None
        return state

    # Otherwise, try conservative extraction
    extracted = extract_intake_fields(last_user_message)
    for field, value in extracted.items():
        if field in state["intake"] and state["intake"][field] is None:
            state["intake"][field] = value

    return state

def intro_node(state: ScoutState) -> ScoutState:
    if state.get("intro_done"):
        return state

    if not state["messages"] or state["messages"][-1]["role"] != "user":
        return state
    
    state["messages"].append({
        "role": "assistant",
        "content": (
            "Hi! Welcome to ITIKKAR Deal Onboarding 👋\n\n"
            "I’m here to help you submit a deal. "
            "Could you tell me a bit about what you’re looking to onboard today?"
        )
    })
    state["intro_done"] = True
    state["phase"] = "confirmation"
    return state
        

def decide_next_missing_field(state: ScoutState) -> str | None:
    for field in MANDATORY_FIELDS:
        if state["intake"].get(field) is None:
            return field
    return None

# def chat_node(state: ScoutState) -> ScoutState:
#     reply = chat_llm(state['messages'])
#     state['messages'].append(
#         {
#             'role':'assistant',
#             'content':reply
#             })
#     user_messages = [m for m in state["messages"] if m["role"] == "user"]
#     if 'deal_title' not in state:
#         if len(user_messages) > 3:
#             title = generate_deal_title(state['messages'])
#             state['deal_title'] = title
#     return state
# def ask_missing_field_node(state: ScoutState) -> ScoutState:
#     missing = decide_next_missing_field(state)

#     if missing:
#         state["messages"].append({
#             "role": "assistant",
#             "content": INTAKE_QUESTIONS[missing]
#         })
#         return state

#     state["messages"].append({
#         "role": "assistant",
#         "content": (
#             "Thanks — I have the key deal details. "
#             "We can continue with additional information when you're ready."
#         )
#     })

#     return state
# def ask_missing_field_node(state: ScoutState) -> ScoutState:
#     missing_field = decide_next_missing_field(state)

#     if missing_field:
#         raw_question = INTAKE_QUESTIONS[missing_field]
#         question = make_conversational(raw_question, state['messages'])
#         state['messages'].append({
#             'role': 'assistant',
#             'content': question
#         })
#         state["current_question"] = missing_field
#         return state

#     state['messages'].append({
#         'role': 'assistant',
#         'content': "Thanks. I have the key details. We can continue when you are ready."
#     })
#     return state

def ask_missing_field_node(state: ScoutState) -> ScoutState:
    # 🚫 Do not ask questions unless the user has just spoken
    if not state.get("intake_confirmed"):
        return state
    
    if not state["messages"] or state["messages"][-1]["role"] != "user":
        return state

    missing_field = decide_next_missing_field(state)

    if missing_field:
        raw_question = INTAKE_QUESTIONS[missing_field]
        question = make_conversational(raw_question, state["messages"])

        state["messages"].append({
            "role": "assistant",
            "content": question
        })
        state["current_question"] = missing_field
        return state

    state["messages"].append({
        "role": "assistant",
        "content": (
            "Thanks — that gives me a clear picture of the deal 👍\n\n"
            "We can continue whenever you’re ready."
        )
    })
    return state


def maybe_generate_title_node(state: ScoutState) -> ScoutState:
    if state.get("deal_title"):
        return state

    # Check mandatory fields
    mandatory_fields = ["company_name", "industry", "deal_type", "deal_size", "geography"]

    if not all(state["intake"].get(f) for f in mandatory_fields):
        return state

    title = generate_deal_title_from_intake(state["intake"])
    state["deal_title"] = title

    return state

# def confirm_intake_node(state: ScoutState) -> ScoutState:
#     if state.get("intake_confirmed"):
#         return state

#     if not state["messages"] or state["messages"][-1]["role"] != "user":
#         return state

#     user_msg = state["messages"][-1]["content"]

#     if user_confirmed_intake(user_msg):
#         state["intake_confirmed"] = True
#         state["phase"] = "intake"

#         # state["messages"].append({
#         #     "role": "assistant",
#         #     "content": (
#         #         "Great — let’s get started 👍\n\n"
#         #         "To begin with, what kind of deal are you looking to onboard?"
#         #     )
#         # })
#         state["messages"].append({
#             "role": "assistant",
#             "content": "Great — let’s get started 👍"
#         })


#     return state

def confirm_intake_node(state: ScoutState) -> ScoutState:
    if state.get("intake_confirmed"):
        return state

    if not state["messages"] or state["messages"][-1]["role"] != "user":
        return state

    user_msg = state["messages"][-1]["content"]

    if user_confirmed_intake(user_msg):
        state["intake_confirmed"] = True
        state["phase"] = "intake"

        # Find first missing mandatory field
        first_field = decide_next_missing_field(state)

        if first_field:
            question = make_conversational(INTAKE_QUESTIONS[first_field])

            state["messages"].append({
                "role": "assistant",
                "content": f"Great — let’s get started 👍\n\n{question}"
            })

            state["current_question"] = first_field
        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Great — looks like we already have the key details 👍"
            })

    return state

# -----------------------------
# Graph definition
# -----------------------------

graph = StateGraph(ScoutState)
graph.add_node("intro", intro_node)
graph.add_node("confirm_intake", confirm_intake_node)
graph.add_node("extract_intake", extract_intake_node)
graph.add_node("maybe_generate_title", maybe_generate_title_node)
graph.add_node("ask_missing", ask_missing_field_node)

graph.set_entry_point("intro")
graph.add_edge("intro", "confirm_intake")
graph.add_edge("confirm_intake", "extract_intake")
graph.add_edge("extract_intake", "maybe_generate_title")
graph.add_edge("maybe_generate_title", "ask_missing")
graph.add_edge("ask_missing", END)

scout_graph = graph.compile()
# graph = StateGraph(ScoutState)

# graph.add_node("extract_intake", extract_intake_node)
# graph.add_node("ask_missing_field", ask_missing_field_node)
# #graph.add_node("chat", chat_node)

# graph.set_entry_point("chat")
# graph.add_edge("chat", "extract_intake")
# graph.add_edge("extract_intake", "ask_missing_field")
# graph.add_edge("ask_missing_field", "chat")
# scout_graph = graph.compile()