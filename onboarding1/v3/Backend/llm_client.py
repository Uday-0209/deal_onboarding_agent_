import os
import json
import requests
from typing import List, Dict
from openai import OpenAI

# -------------------------
# Config
# -------------------------

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1:8b"

USE_OPENAI = bool(os.getenv("USE_OPENAI_LLM"))
OPENAI_MODEL = "gpt-4o-mini"  # safer default


# -------------------------
# System prompts
# -------------------------

CONVERSATION_SYSTEM_PROMPT = """
You are a professional deal intake assistant.

Your role:
- Have a natural, intelligent conversation
- Guide the user to describe their deal
- Ask contextual follow-up questions only when needed
- Do NOT ask rigid form-style questions
- Do NOT repeat information already provided
- Keep responses concise and professional

Do not mention internal processes or data extraction.
"""

TITLE_SYSTEM_PROMPT = """
You generate short, professional deal titles.

Rules:
- Max 8 words
- No numbers
- No marketing language
- Focus on deal type, sector, and geography
- Return ONLY the title text
"""

EXTRACTION_SYSTEM_PROMPT = """
Extract deal intake fields from the user message.

Fields:
- company_name
- industry
- deal_type
- deal_size
- geography
- sector
- contact_person

Rules:
- Extract ONLY explicitly mentioned information
- Do NOT guess or infer
- Return JSON only
- Omit fields you are not confident about
"""


# -------------------------
# Core LLM callers
# -------------------------

def _chat_ollama(messages: List[Dict]) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }

    response = requests.post(
        OLLAMA_CHAT_URL,
        json=payload,
        timeout=120
    )
    response.raise_for_status()

    return response.json()["message"]["content"]


def _chat_openai(messages: List[Dict]) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=300
    )
    return response.choices[0].message.content


def _chat(messages: List[Dict]) -> str:
    if USE_OPENAI:
        return _chat_openai(messages)
    return _chat_ollama(messages)


# -------------------------
# Public API
# -------------------------

def chat_llm(conversation: List[Dict]) -> str:
    """
    Generate the next assistant reply based on full conversation.
    """
    messages = [
        {"role": "system", "content": CONVERSATION_SYSTEM_PROMPT},
        *conversation
    ]
    return _chat(messages)


def extract_intake_fields(user_message: str) -> Dict:
    """
    Extract structured intake fields from a single user message.
    """
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    response = _chat(messages)

    try:
        data = json.loads(response)
        return {k: (v if v else None) for k, v in data.items()}
    except Exception:
        return {}


def generate_deal_title(conversation: List[Dict]) -> str:
    """
    Generate or regenerate a deal title from recent conversation.
    """
    messages = [
        {"role": "system", "content": TITLE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "\n".join(
                f"{m['role']}: {m['content']}"
                for m in conversation
            )
        }
    ]

    title = _chat(messages).strip()
    return title.split("\n")[0]
