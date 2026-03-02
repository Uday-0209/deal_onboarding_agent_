import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

''''Functions to manage the chat seessions and user data in redis'''

def get_user_chats(email:str) -> list['str']:
    key = f"user:{email}:chats"
    chats = redis_client.get(key)
    return json.loads(chats) if chats else []

def add_chat_to_user(email:str, chat_id:str) -> None:
    key = f"user:{email}:chats"
    chats = get_user_chats(email)
    if chat_id not in chats:
        chats.append(chat_id)
        redis_client.set(key, json.dumps(chats))
        
''''chat state helpers'''

def get_chat_state(chat_id:str) -> dict:
    key = f"chat:{chat_id}:state"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def save_chat_state(chat_id:str, state:dict):
    key = f"chat:{chat_id}:state"
    redis_client.set(key, json.dumps(state))

def save_deal(email: str, chat_id: str, deal_data: dict) -> None:
    """Save extracted deal details to Redis"""
    key = f"deal:{email}:{chat_id}"
    redis_client.set(key, json.dumps(deal_data))

def get_deal(email: str, chat_id: str) -> dict:
    """Retrieve saved deal details from Redis"""
    key = f"deal:{email}:{chat_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def create_new_chat_state() -> dict:
    return {
        "messages": [],
        "phase": "intake",
        "deal_title": None,
        "intake": {
            "company_name": None,
            "deal_size": None,
            "industry": None,
            "contact_person": None,
            "deal_type": None,
            "geography": None,
            "sector": None
        }
    }
def get_user_chats_from_redis(email: str) -> list[str]:
    key = f"user:{email}:chats"
    return redis_client.lrange(key, 0, -1)
