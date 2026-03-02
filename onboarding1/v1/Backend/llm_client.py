import os
import json
import requests
from openai import OpenAI

# -----------------------------
# LLM Router (OpenAI or Local LLaMA)
# -----------------------------

SYSTEM_PROMPT = """
You are a language assistant for ITIKKAR.

You do NOT decide conversation flow.
You do NOT ask new questions unless explicitly instructed.
You ONLY respond to the specific task given.

Be concise and professional.
"""

def chat_openai(messages: list[dict]) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages
    )
    return response.choices[0].message.content


def chat_llama(messages: list[dict]) -> str:
    payload = {
        "model": "llama3.1:8b",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": False
    }
    response = requests.post(
        "http://localhost:11434/api/chat",
        json=payload,
        timeout=60
    )
    # return response.json()["message"]["content"]
    data = response.json()
    # Ollama non-streaming response
    if "message" in data and "content" in data["message"]:
        return data["message"]["content"]

    # Ollama completion-style response
    if "response" in data:
        return data["response"]

    raise ValueError(f"Unexpected Ollama response format: {data}")



def chat_llm(messages: list[dict]) -> str:
    if os.getenv("OPENAI_API_KEY"):
        return chat_openai(messages)
    return chat_llama(messages)


# -----------------------------
# Conservative Intake Extraction
# -----------------------------
def make_conversational(question: str, context: list[dict]) -> str:
    prompt = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + (
                "Rewrite the following question in a friendly, natural tone.\n"
                "Rules:\n"
                "- Do NOT add new questions\n"
                "- Do NOT add explanations\n"
                "- Do NOT change intent\n"
                "- Output ONLY the rewritten question"
            )
        },
        {
            "role": "user",
            "content": f"Original question: {question}"
        }
    ]

    return chat_llm(prompt).strip()


def extract_intake_fields(text: str) -> dict:
    """
    Returns a dict like:
    {
        "deal_type": "equity",
        "deal_size": "200 crores"
    }
    """
    prompt = [
        {
            "role": "system",
            "content": (
                "Extract any deal intake fields mentioned in the text.\n"
                "Return a JSON object with keys from:\n"
                "company_name, industry, deal_type, deal_size, geography, sector, contact_person.\n"
                "Only include fields that are explicitly mentioned.\n"
                "Return ONLY valid JSON."
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]

    raw = chat_llm(prompt)

    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    prompt = [
        {
            "role": "system",
            "content": (
                "Extract deal intake fields from the user message.\n\n"
                "Fields:\n"
                "- deal_type\n"
                "- deal_size\n"
                "- geography\n"
                "- sector\n\n"
                "Rules:\n"
                "- Only extract fields explicitly stated\n"
                "- Do NOT guess or infer\n"
                "- Return JSON only\n"
                "- Omit fields you are not confident about"
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = chat_llm(prompt)

    try:
        return json.loads(response)
    except Exception:
        return {}

def generate_deal_title_from_intake(intake: dict) -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "You generate short, professional deal titles for an investment platform.\n\n"
                "Rules:\n"
                "- Max 8 words\n"
                "- Neutral tone\n"
                "- No marketing language\n"
                "- Prefer format: Company / Deal Type / Geography\n"
                "- Do not include confidential details\n"
                "- Return ONLY the title text"
            )
        },
        {
            "role": "user",
            "content": f"Deal details:\n{intake}"
        }
    ]

    return chat_llm(prompt).strip()
