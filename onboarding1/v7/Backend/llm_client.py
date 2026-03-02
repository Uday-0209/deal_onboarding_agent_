import os
import json
import requests
from typing import List, Dict
from openai import OpenAI
import re
from v7.Backend.prompts import CONVERSATION_SYSTEM_PROMPT, TITLE_SYSTEM_PROMPT, EXTRACTION_SYSTEM_PROMPT
# -------------------------
# Config
# -------------------------

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
#OLLAMA_MODEL = "gemma3"
OLLAMA_MODEL = "llama3.1:8b"

USE_OPENAI = bool(os.getenv("USE_OPENAI_LLM"))
OPENAI_MODEL = "gpt-4o-mini"  # safer default


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

'''Works for openai not for the llama'''
# def extract_intake_fields(user_message: str) -> Dict: 
#     """
#     Extract structured intake fields from a single user message.
#     """
#     messages = [
#         {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
#         {"role": "user", "content": user_message}
#     ]

#     response = _chat(messages)
#     print("Raw extraction response:", response)

#     try:
#         data = json.loads(response)
#         return {k: (v if v else None) for k, v in data.items()}
#     except Exception as e:
#         print("Json parse failed", e)
#         return {}
def extract_intake_fields(message) -> dict:
    messages = [
        {'role':"system", "content":EXTRACTION_SYSTEM_PROMPT},
        {'role':'user', 
         "content":message}
    ]

    response = _chat(messages)

    print("Raw llama output", response)

    # cleaned = response.strip()

    # if cleaned.startswith("```"):
    #     cleaned = re.sub(r"^```(?:json)?", "", cleaned)
    #     cleaned = re.sub(r"```$", "", cleaned)
    #     cleaned = cleaned.strip()
    
    match = re.search(r"\{.*?\}", response, re.DOTALL)
    
    if not match:
        print("no json found in response")
        return {}
    
    json_str = match.group()

    try:
        data = json.loads(json_str)
        print("Json Extracted data", data)
        return {k: v for k, v in data.items() if v is not None}
    except Exception as e:
        print("Json purse failed")
        print("error", e)
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
