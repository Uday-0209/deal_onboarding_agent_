from langgraph.graph import StateGraph, END
from typing import TypedDict

from v5.Backend.redis_client import (
    append_message,
    get_messages,
    update_intake_fields,
    is_deal_complete, 
    get_deal_meta,
    get_intake_field,
    mark_deal_completed,
    update_deal_meta_data,
    REQUIRED_FIELDS
    
)
from v5.Backend.summary_generator import generate_deal_summary
from v5.Backend.summary_store import store_deal_summary
from v5.Backend.llm_client import (
    chat_llm,
    extract_intake_fields,
)

# -------------------------
# Graph state
# -------------------------

class GraphState(TypedDict):
    deal_id: str
    last_user_message: str


# -------------------------
# Nodes
# -------------------------

def llm_reply_node(state: GraphState) -> GraphState:
    print("🔥 LLM NODE CALLED")
    deal_id = state["deal_id"]

    messages = get_messages(deal_id)
    conversation = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    intake = get_intake_field(deal_id)
    missing = [
        f for f in REQUIRED_FIELDS if not intake.get(f)
    ]
    system_prompt = f"""
    You are a professional deal intake assistant.

    Missing required fields:
    {missing if missing else "None"}

    Rules:
    - If missing fields exist, ask natural follow-up questions to collect them
    - Ask ONLY about missing fields
    - Do NOT repeat already collected information
    - Do NOT assume or infer values
    - NEVER say the deal is complete unless missing fields is empty
    - If no fields are missing, politely confirm completion
    """
    llm_messages = [
        {'role':'system', 'content':system_prompt},
        *conversation
    ]

    reply = chat_llm(llm_messages)
    print("🔥 LLM REPLY:", reply)

    append_message(state["deal_id"], "assistant", reply)
    return state


def extraction_node(state: GraphState) -> GraphState:
    deal_id = state["deal_id"]
    extracted = extract_intake_fields(state["last_user_message"])
    
    if not isinstance(extracted, dict):
        return state
    
    cleaned = {k: v for k, v in extracted.items() if v}
    
    if not cleaned:
        return state
    
    update_intake_fields(deal_id, cleaned)
    
    update_deal_meta_data(deal_id, cleaned)

    # if isinstance(extracted, dict):
    #     cleaned = {k: v for k, v in extracted.items() if v is not None}
    #     if cleaned:
    #         update_intake_fields(state["deal_id"], cleaned)

    return state

def completion_node(state):
    deal_id = state["deal_id"]

    meta = get_deal_meta(deal_id)

    # 🔒 Guard: already completed → do nothing
    if meta.get("completed") == "true":
        return state

    # ✅ Check if deal is now complete
    if is_deal_complete(deal_id):
        # 1️⃣ Mark completed
        mark_deal_completed(deal_id)

        # 2️⃣ Closing message (ONE TIME)
        append_message(
            deal_id,
            "assistant",
            "Thank you for onboarding the deal."
        )

        # 3️⃣ Generate + store summary (REAL-TIME)
        intake = get_intake_field(deal_id)
        summary = generate_deal_summary(deal_id)
        print('completeion_node:',summary)
        store_deal_summary(deal_id, summary, intake)

    return state

# -------------------------
# Graph definition
# -------------------------

graph = StateGraph(GraphState)

graph.add_node("llm_reply", llm_reply_node)
graph.add_node("extract", extraction_node)
graph.add_node("complete", completion_node)

graph.set_entry_point("extract")

graph.add_edge("extract", "complete")
graph.add_edge("complete", "llm_reply")
graph.add_edge("llm_reply", END)
hybrid_graph = graph.compile()
