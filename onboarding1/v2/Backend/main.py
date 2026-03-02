from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from Backend.graph import scout_graph
from Backend.redis_client import (
    get_user_chats,
    add_chat_to_user,
    get_chat_state,
    save_chat_state,
    create_new_chat_state,
    save_deal,
    get_deal
)
import uuid
import json
import requests

app = FastAPI()

#SESSIONS = {}

class ChatRequest(BaseModel):
    email: str
    chat_id: str | None = None
    message: str
    
class ChatResponse(BaseModel):
    chat_id: str
    reply: str

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"


def ollama_stream(messages: list[dict]):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True
    }

    with requests.post(
        OLLAMA_CHAT_URL,
        json=payload,
        stream=True,
        timeout=300
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            data = json.loads(line.decode("utf-8"))

            if "message" in data and "content" in data["message"]:
                yield data["message"]["content"]

            if data.get("done"):
                break

@app.post('/chat', response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    email = request.email.lower().strip()
    if request.chat_id:
        chat_id = request.chat_id
    else:
        chat_id = str(uuid.uuid4())
        add_chat_to_user(email, chat_id)
        
    state = get_chat_state(chat_id)
    if state is None:
        state = create_new_chat_state()
        save_chat_state(chat_id, state)
        
    state['messages'].append({
        'role':'user',
        'content':request.message
        })
    
    new_state = scout_graph.invoke(state)
    
    save_chat_state(chat_id, new_state)
    
    # Auto-save deal details after each message
    if new_state.get('intake'):
        deal_data = {
            "deal_title": new_state.get('deal_title'),
            "intake": new_state.get('intake'),
            "chat_id": chat_id,
            "messages_count": len(new_state.get('messages', []))
        }
        save_deal(email, chat_id, deal_data)
    
    reply = new_state['messages'][-1]['content']
    
    return ChatResponse(
        chat_id = chat_id,
        reply = reply
    )

@app.get("/user_chats")
def list_user_chats(email:str):
    chats = get_user_chats(email.lower().strip())
    return {"chats":chats}

@app.get("/chat_state")
def load_chat_state(chat_id:str):
    state = get_chat_state(chat_id)
    return state or {"messages":[], 'phase':'start'}

@app.get("/deal")
def get_deal_endpoint(email: str, chat_id: str):
    """Retrieve saved deal details"""
    email = email.lower().strip()
    deal = get_deal(email, chat_id)
    return deal or {"status": "error", "message": "Deal not found"}

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    email = request.email.lower().strip()

    chat_id = request.chat_id or str(uuid.uuid4())
    if not request.chat_id:
        add_chat_to_user(email, chat_id)

    state = get_chat_state(chat_id)
    if state is None:
        state = create_new_chat_state()

    # store user message immediately
    state["messages"].append({
        "role": "user",
        "content": request.message
    })
    save_chat_state(chat_id, state)

    response = StreamingResponse(
    ollama_stream(state["messages"]),
    media_type="text/plain"
    )
    response.headers["X-Chat-Id"] = chat_id
    return response


# @app.get("/user_chats")
# def get_user_chats(email: str = Query(...)):
#     email = email.lower().strip()

#     chats = get_user_chats_from_redis(email)

#     return {
#         "email": email,
#         "chats": chats
#     }
