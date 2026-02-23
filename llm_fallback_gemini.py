import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Expect full resource name like: models/gemini-2.5-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")

def generate(system: str, user: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")

    url = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent"
    params = {"key": GEMINI_API_KEY}

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{system}\n\nUser: {user}"}]}
        ],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 450},
    }

    r = requests.post(url, params=params, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini API error {r.status_code}: {r.text}")

    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()