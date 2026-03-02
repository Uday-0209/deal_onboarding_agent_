from langgraph.graph import StateGraph, END
from typing import TypedDict

from v3.Backend.redis_client import (
    append_message,
    get_messages,
    update_intake_fields,
)

from v3.Backend.llm_client import (
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

    messages = get_messages(state["deal_id"])
    llm_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    reply = chat_llm(llm_messages)
    print("🔥 LLM REPLY:", reply)

    append_message(state["deal_id"], "assistant", reply)
    return state


def extraction_node(state: GraphState) -> GraphState:
    extracted = extract_intake_fields(state["last_user_message"])

    if isinstance(extracted, dict):
        cleaned = {k: v for k, v in extracted.items() if v is not None}
        if cleaned:
            update_intake_fields(state["deal_id"], cleaned)

    return state


# -------------------------
# Graph definition
# -------------------------

graph = StateGraph(GraphState)

graph.add_node("llm_reply", llm_reply_node)
graph.add_node("extract", extraction_node)

graph.set_entry_point("llm_reply")
graph.add_edge("llm_reply", "extract")
graph.add_edge("extract", END)

hybrid_graph = graph.compile()
