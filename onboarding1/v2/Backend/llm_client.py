import os
import requests
import re
from openai import OpenAI
from typing import List

System_prompt = """
You are the Deal Agent for ITIKKAR.
Your role is to guide users through deal submission.
Ask clear, structured questions.
Here ITTIKAR is middle men who have the customers and dels.
Do not evaluate or approve deals.
Keep responses concise.
"""

def chat_openai(model, messages: List[dict], temperature=0.7, max_tokens=150):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in environment variables.")
    
    client = OpenAI(api_key=openai_api_key)
    
    messages = [
        {'role': 'system', 'content': System_prompt},
        *messages
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message['content']

def chat_llama(messages:List[dict], temperature=0.7, max_tokens=150):
    payload = {
        "model": 'llama3.1:8b',
        "messages": [
            {'role':'system', 'content': System_prompt},
            *messages
        ],
        'stream':False,
    }
    response = requests.post(
        "http://localhost:11434/api/chat",
        json=payload   
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]

def chat_llm(messages: List[dict]) -> str:
    if os.getenv("USE_OPENAI_LLM"):
        return chat_openai(model="gpt-4", messages=messages)
    else:
        return chat_llama(messages=messages)
    
#print(chat_llm([{'role':'user', 'content':'Hello, how can you assist me with deal submission?'}]))

def generate_title_llm(messages: List[dict]) -> str:
    if os.getenv("USE_OPENAI_LLM"):
        return chat_openai(model="gpt-4", messages=messages)
    else:
        return chat_llama(messages=messages)

import re

def generate_deal_title(messages: List[dict]) -> str:
    conversation = '\n'.join([f"{m['role'].capitalize()}: {m['content']}" for m in messages[-6:]])
    prompt = [
        {
            'role': 'system',
            'content': 'You are a helpful assistant that generates concise deal titles based on conversations.'
        },
        {
            'role': 'user',
            'content': f'Generate a short deal title (max 8 words) based on the following conversation. Focus on deal type, sector or asset, and geography if available. Do not include numbers or marketing language. Return only the title.\n\n{conversation}'
        }
    ]
    response = generate_title_llm(prompt)
    # Clean the response
    title = response.strip()
    # Remove any extra text like "Title:" or quotes
    title = re.sub(r'^(Title|Deal Title)[:\-]*\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^["\']|["\']$', '', title)  # Remove surrounding quotes
    title = title.split('\n')[0].strip()  # Take first line
    return title if title else "Untitled Deal"

def extract_intake_fields(user_message: str) -> dict:
    prompt = [{
        'role':'system',
        'content':(
             "Extract deal intake fields from the user message.\n\n"
                "Fields:\n"
                "- company_name\n"
                "- industry\n"
                "- contact_person\n"                
                "- deal_type\n"
                "- deal_size\n"
                "- geography\n"
                "- sector\n\n"
                "Rules:\n"
                "- Only extract fields that are explicitly stated\n"
                "- Do not guess or infer\n"
                "- Return JSON only\n"
                "- Omit fields you are not confident about"
        )
    }
              ,{
        'role':'user',
        'content':user_message
        }
    ]
    
    response = chat_llm(prompt)
    try:
        import json
        return json.loads(response)
    except Exception:
        return {}