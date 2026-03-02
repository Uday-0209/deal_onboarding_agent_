from langgraph.graph import StateGraph, END
from typing import TypedDict
from v8.Backend.prompts import GUARDRAILS_SYSTEM_PROMPT,DOCUMENT_REQUEST_PROMPT, DOC_AWAITING_PROMPT
from v8.Backend.redis_client import (
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
from v8.Backend.summary_generator import generate_deal_summary
from v8.Backend.summary_store import store_deal_summary
from v8.Backend.llm_client import (
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
    
    meta = get_deal_meta(deal_id)
    
    intake = get_intake_field(deal_id)
    
    missing = [
        f for f in REQUIRED_FIELDS if not intake.get(f)
    ]
    documents_requested = meta.get("documents_requested") == "true"
    documents_uploaded = meta.get('documents_uploaded') == 'true'
    if missing:
        system_prompt = f"{GUARDRAILS_SYSTEM_PROMPT} Missing fields: {missing if missing else 'None'}" 
    elif not documents_requested:
        system_prompt = DOCUMENT_REQUEST_PROMPT
    
    elif documents_requested and not documents_uploaded:
        system_prompt = DOC_AWAITING_PROMPT
        
        
        update_deal_meta_data(deal_id, {
            "documents_requested":"true"
        })
        # update_deal_meta_data(
        #      deal_id,
        #     {
        #         "documents_uploaded": "true",
        #         "deal_status": "processing"
        #     }
        # )

    else:
        system_prompt = GUARDRAILS_SYSTEM_PROMPT
    
    conversation = [
        {"role":m["role"], "content":m["content"]}
        for m in messages
    ]    
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
    
    messages = get_messages(deal_id)
    # current_state = get_intake_field(deal_id)
    
    # last_user_message = state['last_user_message']
    #messages = get_messages(deal_id)
    
    conversation_text = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in messages
    )
    extracted = extract_intake_fields(
       conversation_text
    )
    
    if not isinstance(extracted, dict):
        return state    
  
    cleaned = {k: v for k, v in extracted.items() if v}
    
    # for field, value in extracted.items():
    #     if not value:
    #         continue
        
    #     if str(value).lower() in last_user_message:
    #         validated_updates[field] = value
            
    # if not validated_updates:
    #     return state
    
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
    # if meta.get("completed") == "true":
    #     return state

    # ✅ Check if deal is now complete
    if is_deal_complete(deal_id):
        # 1️⃣ Mark completed
        mark_deal_completed(deal_id)

        # 2️⃣ Closing message (ONE TIME)
        # append_message(
        #     deal_id,
        #     "assistant",
        #     "Thank you for onboarding the deal."
        # )
                
        # 3️⃣ Generate + store summary (REAL-TIME)
        intake = get_intake_field(deal_id)
        summary = generate_deal_summary(deal_id)
        print('completeion_node:',summary)
        store_deal_summary(deal_id, summary, intake)
        if meta.get("documents_requested") != "true":
            append_message(
                deal_id,
                "assistant",
                "All required deal details are captured. "
                "Please upload supporting documents such as pitch deck, term sheet, "
                "financial projections, feasibility report, etc."
            )
            update_deal_meta_data(deal_id, {
                "documents_requested": "true"
            })

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
