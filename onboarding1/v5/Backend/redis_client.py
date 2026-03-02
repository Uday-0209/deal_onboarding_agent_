import redis
import json
from datetime import datetime
from typing import Dict, List, Optional
#from datetime import datetime

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

REQUIRED_FIELDS = {
    "company_name",
    "industry",
    "deal_type",
    "deal_size",
    "geography",
    "contact_person"
}

# -------------------------
# Utils
# -------------------------

def _now() -> str:
    return datetime.utcnow().isoformat()


# -------------------------
# Deal creation / loading
# -------------------------

def create_deal(deal_id: str, email: str) -> None:
    meta_key = f"deal:{deal_id}:meta"
    intake_key = f"deal:{deal_id}:intake"

    redis_client.hset(meta_key, mapping={
        "deal_id": deal_id,
        "deal_title": "",
        "completed": "false",
        "message_count": 0,
        "created_at": _now(),
        "updated_at": _now()
    })

    redis_client.hset(intake_key, mapping={
        "company_name": "",
        "industry": "",
        "deal_type": "",
        "deal_size": "",
        "geography": "",
        "contact_person": ""
    })

    redis_client.sadd(f"user:{email}:deals", deal_id)


def deal_exists(deal_id: str) -> bool:
    return redis_client.exists(f"deal:{deal_id}:meta") == 1


# -------------------------
# Messages
# -------------------------

def append_message(deal_id: str, role: str, content: str) -> None:
    message = {
        "role": role,
        "content": content,
        "timestamp": _now()
    }

    redis_client.rpush(
        f"deal:{deal_id}:messages",
        json.dumps(message)
    )

    redis_client.hincrby(f"deal:{deal_id}:meta", "message_count", 1)
    redis_client.hset(f"deal:{deal_id}:meta", "updated_at", _now())


def get_messages(deal_id: str) -> List[Dict]:
    raw = redis_client.lrange(f"deal:{deal_id}:messages", 0, -1)
    return [json.loads(m) for m in raw]


# -------------------------
# Intake fields
# -------------------------

def get_intake(deal_id: str) -> Dict[str, Optional[str]]:
    data = redis_client.hgetall(f"deal:{deal_id}:intake")
    return {k: (v if v else None) for k, v in data.items()}


def update_intake_fields(deal_id: str, extracted: Dict[str, str]) -> None:
    intake_key = f"deal:{deal_id}:intake"

    for field, value in extracted.items():
        # if redis_client.hget(intake_key, field) in ("", None):
        #     redis_client.hset(intake_key, field, value)
        
        if value is (None, "", "null"):
            continue
        
        current = redis_client.hget(intake_key, field)
        
        if current in ("", None):
            redis_client.hset(intake_key, field, str(value))

    redis_client.hset(f"deal:{deal_id}:meta", "updated_at", _now())


# -------------------------
# Deal metadata
# -------------------------

def update_deal_title(deal_id: str, title: str) -> None:
    redis_client.hset(f"deal:{deal_id}:meta", "deal_title", title)
    redis_client.hset(f"deal:{deal_id}:meta", "updated_at", _now())


def mark_deal_completed(deal_id: str) -> None:
    redis_client.hset(f"deal:{deal_id}:meta", "completed", "true")
    redis_client.hset(f"deal:{deal_id}:meta", "updated_at", _now())


def get_deal_meta(deal_id: str) -> Dict:
    return redis_client.hgetall(f"deal:{deal_id}:meta")


# -------------------------
# User deals
# -------------------------

def get_user_deals(email: str) -> List[str]:
    return list(redis_client.smembers(f"user:{email}:deals"))

def get_intake_field(deal_id: str) -> dict:
    intake_key = f"deal:{deal_id}:intake"
    data = redis_client.hgetall(intake_key)

    # Redis returns bytes sometimes, normalize to str
    return {
        k.decode() if isinstance(k, bytes) else k:
        v.decode() if isinstance(v, bytes) else v
        for k, v in data.items()
    }
    
#------------------------------------
# Mark Deal As Completed
#------------------------------------

def is_deal_complete(deal_id: str) -> bool:
    intake = get_intake_field(deal_id)
    
    return all(
        intake.get(field)
        for field in REQUIRED_FIELDS
    )

def update_deal_meta_data(deal_id: str, fields: dict) -> None:
    if not fields:
        return 
    
    redis_client.hset(
        f"deal:{deal_id}:meta",
        mapping = fields
    )
    
    redis_client.hset(
        f"deal:{deal_id}:meta",
        "updated_at",
        _now()
    )