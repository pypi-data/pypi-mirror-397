import requests
import json
import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

def call_ollama(model: str, prompt: str, system: str = "") -> str:
    """
    Call Ollama API for local inference.
    Returns the generated text.
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: Ollama returned {response.status_code}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def is_ollama_available() -> bool:
    try:
        requests.get(OLLAMA_HOST, timeout=2)
        return True
    except:
        return False
