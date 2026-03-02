from typing import List, TypedDict, Dict, Optional
from langgraph.graph import StateGraph, END
from Backend.llm_client import chat_llm, generate_deal_title, extract_intake_fields

MANDATORY_FIELDS = ["company_name","industry","deal_type", "deal_size", "geography"]
OPTIONAL_FIELDS = ["sector","contact_person"]

INTAKE_QUESTIONS = {
    "deal_type": "What type of deal is this? (e.g. debt, equity, project finance)",
    "deal_size": "What is the approximate deal size?",
    "geography": "Which geography or country does this deal relate to?",
    "sector": "What sector or asset class is this deal in?",
    "company_name": "What is the name of the company involved in the deal?",
    "industry": "What industry does the company operate in?",
    "contact_person": "Who is the main contact person for this deal?"
}

class ScoutState(TypedDict):
    messages: List[dict]
    phase: str
    deal_title: Optional[str]
    intake:Dict[str, Optional[str]]
    
def chat_node(state: ScoutState) -> ScoutState:
    #reply = chat_llm(state['messages'])
    state['messages'].append(
        {
            'role':'assistant',
            'content':reply
            })
    user_messages = [m for m in state["messages"] if m["role"] == "user"]
    if 'deal_title' not in state:
        if len(user_messages) > 3:
            title = generate_deal_title(state['messages'])
            state['deal_title'] = title
    return state

def extract_intake_node(state:ScoutState) -> ScoutState:
    last_user_message = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "user"),
        None
    )
    if not last_user_message:
        return state
    
    extraxted = extract_intake_fields(last_user_message)
    
    for field, value in extraxted.items():
        if field in state['intake'] and state['intake'][field] is None:
            state['intake'][field] = value
    
    return state

def decide_next_missing_field(state:ScoutState) -> str | None:
    for field in MANDATORY_FIELDS:
        if state['intake'].get(field) is None:
            return field
    return None

def ask_missing_field_node(state:ScoutState) -> ScoutState:
    missing_field = decide_next_missing_field(state)
    if missing_field:
        question = INTAKE_QUESTIONS[missing_field]
        state['messages'].append({
            'role':'assistant',
            'content':question
        })
        return state
    state['messages'].append({
        'role':'assistant',
        'content':"Thanks. I have the key details.we can continue when you are ready."
    })
    return state 


graph = StateGraph(ScoutState)

graph.add_node("extract_intake", extract_intake_node)
graph.add_node("ask_missing_field", ask_missing_field_node)
graph.add_node("chat", chat_node)

graph.set_entry_point("chat")
graph.add_edge("chat", "extract_intake")
graph.add_edge("extract_intake", "ask_missing_field")
graph.add_edge("ask_missing_field", "chat")
scout_graph = graph.compile()