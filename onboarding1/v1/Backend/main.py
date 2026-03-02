
from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from v1.Backend.graph import scout_graph
from v1.Backend.redis_client import (
    get_user_chats,
    add_chat_to_user,
    get_chat_state,
    save_chat_state,
    create_new_chat_state,
)

app = FastAPI()

# -----------------------------
# Models
# -----------------------------

class ChatRequest(BaseModel):
    email: str
    chat_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    chat_id: str
    reply: str


# -----------------------------
# Endpoints
# -----------------------------

# @app.post("/chat", response_model=ChatResponse)
# def chat_endpoint(req: ChatRequest):
#     email = req.email.lower().strip()

#     # Resolve or create chat
#     if req.chat_id:
#         chat_id = req.chat_id
#     else:
#         chat_id = str(uuid.uuid4())
#         add_chat_to_user(email, chat_id)

#     # Load or init state
#     state = get_chat_state(chat_id)
#     if state is None:
#         state = create_new_chat_state()

#     # Append user message
#     # state["messages"].append({
#     #     "role": "user",
#     #     "content": req.message
#     # })

#     # # Run LangGraph
#     # new_state = scout_graph.invoke(state)

#     # # Persist state
#     # save_chat_state(chat_id, new_state)

#     # reply = new_state["messages"][-1]["content"]
#     if not state["messages"]:
#         state = scout_graph.invoke(state)  # runs intro_node

#     # Now append user message
#     state["messages"].append({
#         "role": "user",
#         "content": req.message
#     })

#     # Run graph again for intake logic
#     state = scout_graph.invoke(state)

#     save_chat_state(chat_id, state)

#     reply = state["messages"][-1]["content"]

#     return ChatResponse(chat_id=chat_id, reply=reply)
@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    email = req.email.lower().strip()

    # Resolve or create chat
    if req.chat_id:
        chat_id = req.chat_id
    else:
        chat_id = str(uuid.uuid4())
        add_chat_to_user(email, chat_id)

    # Load or init state
    state = get_chat_state(chat_id)
    if state is None:
        state = create_new_chat_state()

    # ✅ STEP 1: If intro not done, run graph FIRST
    if not state.get("intro_done"):
        state = scout_graph.invoke(state)
        save_chat_state(chat_id, state)

    # ✅ STEP 2: Append user message
    state["messages"].append({
        "role": "user",
        "content": req.message
    })

    # ✅ STEP 3: Run graph ONCE to respond
    state = scout_graph.invoke(state)

    # Persist
    save_chat_state(chat_id, state)

    #reply = state["messages"][-1]["content"]
    reply = next(
        (m["content"] for m in reversed(state["messages"]) if m["role"] == "assistant"),
        "Thanks — let’s continue."  
        )

    return {
        "chat_id": chat_id,
        "reply": reply
    }


@app.get("/user_chats")
def list_user_chats(email: str):
    return {"chats": get_user_chats(email.lower().strip())}


@app.get("/chat_state")
def load_chat_state(chat_id: str):
    return get_chat_state(chat_id) or create_new_chat_state()
