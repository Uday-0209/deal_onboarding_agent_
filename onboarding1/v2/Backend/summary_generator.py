import requests
import json

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"

SYSTEM_PROMPT = """
You are generating an internal deal summary for an investment platform.

Rules:
- Use ONLY the information provided
- Do NOT guess or infer missing details
- Use neutral, professional language
- Write a concise descriptive paragraph
- Do NOT include marketing language
- Do NOT include confidential identifiers

Keep summary around 200 words.
"""

def generate_deal_summary(intake:dict) -> str:
    """
    Generate a single descriptive deal summary
    based on structured intake fields.
    """

    user_prompt = f"""
Deal information:
- Deal type: {intake.get("deal_type") or "Not specified"}
- Deal size: {intake.get("deal_size") or "Not specified"}
- Geography: {intake.get("geography") or "Not specified"}
- Sector: {intake.get("sector") or "Not specified"}

Generate the deal summary:
"""
    payload = {
        'model': MODEL_NAME,
        "messages":[
            {'role':'system', 'content': SYSTEM_PROMPT},
            {'role':'user', 'content': user_prompt}
        ],
        "stream":False
    }
    
    response = requests.post(
        OLLAMA_CHAT_URL,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    
    data = response.json()
    
    summary = data["message"]["content"]
    
    return summary

# if __name__ == "__main__":
#     intake = {
#         "deal_type": "Equity",
#         "deal_size": "$10M",
#         "geography": "India",
#         "sector": "Renewable Energy"
#     }
#     print(generate_deal_summary(intake))