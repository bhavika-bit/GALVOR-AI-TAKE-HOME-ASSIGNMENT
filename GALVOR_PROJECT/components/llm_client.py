import os
import requests
from dotenv import load_dotenv
load_dotenv()

class LLMClient:
    """Optional Gemini/Groq API wrapper. The app remains usable without an API key."""
    def __init__(self, provider="none", model=None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "none")).lower().strip()
        self.model = model

    def complete(self, system, user):
        try:
            if self.provider == "gemini":
                key = os.getenv("GEMINI_API_KEY")
                if not key: return None
                model = self.model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                payload = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"parts": [{"text": user}]}], "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}}
                response = requests.post(url, params={"key": key}, json=payload, timeout=60)
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            if self.provider == "groq":
                key = os.getenv("GROQ_API_KEY")
                if not key: return None
                model = self.model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": model, "temperature": 0.2, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}, timeout=60)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            # Fail closed to deterministic local fallbacks; never stop the full dashboard for an LLM outage.
            print(f"Optional LLM call failed: {type(exc).__name__}: {exc}")
        return None
