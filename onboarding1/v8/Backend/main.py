from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from pydantic import BaseModel
import uuid
import shutil
from v8.Backend.redis_client import (
    create_deal,
    deal_exists,
    append_message,
    get_messages,
    get_deal_meta,
    get_user_deals,
    update_deal_meta_data
)

from v8.Backend.graph import hybrid_graph
from v8.Backend.llm_client import chat_llm
from v8.Backend.document_processor import process_document
from typing import Optional, List
from v8.Backend.vectore_extractor import search_deals
import os
import json

app = FastAPI()

UPLOAD_DIR = "upload_docs"

os.makedirs(UPLOAD_DIR, exist_ok= True)
# -------------------------
# Schemas
# -------------------------

class ChatRequest(BaseModel):
    email: str
    deal_id: str | None = None
    message: str   


class ChatResponse(BaseModel):
    deal_id: str
    reply: str
    completed: bool
    documents_requested: bool
    documents_uploaded: bool 

class DealListItem(BaseModel):
    deal_id:str
    title:str
    updated_at: Optional[str]
# -------------------------
# Chat endpoint
# -------------------------

# @app.post("/chat", response_model=ChatResponse)
# def chat(request: ChatRequest):
#     email = request.email.lower().strip()

#     # 1️⃣ Create or load deal
#     if request.deal_id and deal_exists(request.deal_id):
#         deal_id = request.deal_id
#     else:
#         deal_id = str(uuid.uuid4())
#         create_deal(deal_id, email)

#     # 2️⃣ Append user message
#     append_message(deal_id, "user", request.message)

#     # 3️⃣ Invoke hybrid graph
#     graph_state = {
#         "deal_id": deal_id,
#         "last_user_message": request.message
#     }

#     result = hybrid_graph.invoke(graph_state)

#     # 4️⃣ Fetch messages & meta
#     messages = get_messages(deal_id)
#     meta = get_deal_meta(deal_id)
#     completed = meta.get("completed") == "true"

#     # 5️⃣ If completed → send closing message
#     if completed:
#         closing_prompt = [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a professional deal assistant. "
#                     "Politely close the conversation, confirming that "
#                     "all required details have been captured."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": "Please close the conversation."
#             }
#         ]

#         closing_message = chat_llm(closing_prompt)
#         append_message(deal_id, "assistant", closing_message)

#         return ChatResponse(
#             deal_id=deal_id,
#             reply=closing_message,
#             completed=True
#         )

#     # 6️⃣ Normal reply (last assistant message)
#     last_reply = next(
#         m["content"] for m in reversed(messages)
#         if m["role"] == "assistant"
#     )

#     return ChatResponse(
#         deal_id=deal_id,
#         reply=last_reply,
#         completed=False
#     )
# @app.post("/chat", response_model=ChatResponse)
# def chat(request: ChatRequest):
#     email = request.email.lower().strip()

#     # 1️⃣ Create or load deal
#     if request.deal_id and deal_exists(request.deal_id):
#         deal_id = request.deal_id
#     else:
#         deal_id = str(uuid.uuid4())
#         create_deal(deal_id, email)

#     # 2️⃣ Append user message
#     append_message(deal_id, "user", request.message)

#     # 3️⃣ Run graph ONCE (side effects only)
#     hybrid_graph.invoke({
#         "deal_id": deal_id,
#         "last_user_message": request.message
#     })

#     # 4️⃣ Fetch last assistant message safely
#     messages = get_messages(deal_id)
#     assistant_messages = [
#         m["content"] for m in messages if m["role"] == "assistant"
#     ]

#     reply = assistant_messages[-1] if assistant_messages else (
#         "Sorry — I couldn’t respond just now."
#     )

#     # 5️⃣ Return immediately
#     return ChatResponse(
#         deal_id=deal_id,
#         reply=reply,
#         completed=False
#     )
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    email = request.email.lower().strip()

    # 1️⃣ Create or load deal
    if request.deal_id and deal_exists(request.deal_id):
        deal_id = request.deal_id
    else:
        deal_id = str(uuid.uuid4())
        create_deal(deal_id, email)

    # 2️⃣ If deal already completed → return final message
    meta = get_deal_meta(deal_id)
    # if meta.get("completed") == "true":
    #     return ChatResponse(
    #         deal_id=deal_id,
    #         reply="Thank you for onboarding the deal.",
    #         completed=True
    #     )
    
    # if meta.get("completed") == 'true':
    #     return state
    
    # 3️⃣ Append user message
    append_message(deal_id, "user", request.message)

    # 4️⃣ Run graph ONCE
    hybrid_graph.invoke({
        "deal_id": deal_id,
        "last_user_message": request.message
    })

    # 5️⃣ Reload meta (graph may have completed it)
    meta = get_deal_meta(deal_id)

    messages = get_messages(deal_id)
    assistant_messages = [
        m["content"] for m in messages if m["role"] == "assistant"
    ]

    reply = assistant_messages[-1] if assistant_messages else (
        "Thank you for onboarding the deal."
    )

    return ChatResponse(
        deal_id=deal_id,
        reply=reply,
        completed=(meta.get("completed") == "true"),
        documents_requested = (meta.get('documents_requested') == 'true'),
        documents_uploaded = (meta.get("documents_uploaded") == 'true')
    )

@app.get("/deals", response_model=list[DealListItem])
def list_deals(email: str):
    deal_ids = get_user_deals(email.lower().strip())
    
    deals = []
    for deal_id in deal_ids:
        meta = get_deal_meta(deal_id) or {}
        
        raw_updated_at = meta.get("updated_at")
        
        updated_at = (
            raw_updated_at
            if isinstance(raw_updated_at, str) and raw_updated_at.strip()
            else None
        )
        
        deals.append({
            "deal_id": deal_id,
            "title": meta.get("deal_title")or f"Deal {deal_id[:8]}",
            "updated_at": updated_at
        })
        
    deals.sort(key=lambda d: d["updated_at"], reverse=True)
    return deals

@app.get("/deals/{deal_id}/messages")
def load_deal_messages(deal_id: str):
    return get_messages(deal_id)

@app.get("/search")
def search(query: str):
    return search_deals(query)

# @app.post("/deals/{deal_id}/upload")
# async def upload_document(deal_id: str, background_tasks: BackgroundTasks, intake: str = Form(...),file:UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIR, f"{deal_id}_{file.filename}")
#     contents = await file.read()
#     intake_dict = json.loads(intake)
    
#     with open(file_path, "wb") as buffer:
#         buffer.write(contents)
    
#     update_deal_meta_data(
#         deal_id,
#         {"deal_status": "processing"}
#     )    
#     background_tasks.add_task(
#         process_document, deal_id, file_path, intake_dict
#         )
    
#     return {'status':"Document Processed"}
@app.post("/deals/{deal_id}/upload")
async def upload_document(deal_id: str, background_tasks: BackgroundTasks, file:UploadFile = File(...)):
    print("UPLOAD HIT")
    file_path = os.path.join(UPLOAD_DIR, f"{deal_id}_{file.filename}")
    print("File read complete")
    contents = await file.read()
    #intake_dict = json.loads(intake)
    
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
    
    print("File written")
    
    update_deal_meta_data(
        deal_id,
        {"deal_status": "processing"}
    )    
    background_tasks.add_task(
        process_document, deal_id, file_path
        )
    
    print("Background task added")
    
    return {'status':"Document Processed"}

@app.get("/deals/{deal_id}/meta")
def get_meta(deal_id: str):
    meta = get_deal_meta(deal_id)
    return meta or {}
