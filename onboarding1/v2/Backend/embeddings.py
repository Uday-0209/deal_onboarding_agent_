import requests

OLLAMA_EMBEDDINGS_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "llama3.1:8b"

def generate_embedding(text:str) -> list[float]:
    payload = {
        "model": MODEL_NAME,
        "input": text
    }
    response = requests.post(OLLAMA_EMBEDDINGS_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["embedding"]