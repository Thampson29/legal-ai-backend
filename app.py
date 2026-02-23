import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from safety import classify, canned_response
from llm_fallback_gemini import generate as fallback_generate

load_dotenv()

FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "gemini").lower()

app = FastAPI(title="Legal Awareness Backend (Plain Text + JSON Supported)")

class ChatRes(BaseModel):
    reply: str
    safety: str
    provider: str

SYSTEM_STYLE = (
    "You are a Legal Awareness Assistant for India.\n"
    "Rules:\n"
    "1) Always include: 'This is general information, not legal advice.'\n"
    "2) Use simple language and bullet-point steps.\n"
    "3) Do not help with illegal or harmful actions.\n"
    "4) If unsure, say so and suggest checking official sources or consulting a lawyer/legal aid.\n"
)

def handle_message(user_id: str | None, message: str) -> ChatRes:
    label = classify(message)

    # Safety first: do not call model
    if label in ("illegal", "emergency"):
        return ChatRes(reply=canned_response(label), safety=label, provider="rules")

    # Call fallback model
    reply = fallback_generate(system=SYSTEM_STYLE, user=message)

    # Hard-enforce disclaimer
    if "not legal advice" not in reply.lower():
        reply = "This is general information, not legal advice.\n\n" + reply

    return ChatRes(reply=reply, safety="ok", provider=FALLBACK_PROVIDER)

@app.post("/chat", response_model=ChatRes)
async def chat(request: Request):
    """
    Accepts BOTH:
      - application/json -> {"user_id": "...", "message": "..."}
      - text/plain       -> "your message here"

    Always returns JSON in ChatRes format.
    """
    content_type = (request.headers.get("content-type") or "").lower()

    user_id = None
    message = None

    # A) JSON input
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON. Send {'message': '...'}."},
            )
        user_id = payload.get("user_id")
        message = payload.get("message")

    # B) Plain text input (or anything else)
    else:
        raw = (await request.body()).decode("utf-8", errors="ignore").strip()

        # If client accidentally sent JSON as text/plain, try to parse it
        if raw.startswith("{") and raw.endswith("}"):
            try:
                payload = json.loads(raw)
                user_id = payload.get("user_id")
                message = payload.get("message")
            except Exception:
                message = raw
        else:
            message = raw

    if not message:
        return JSONResponse(
            status_code=400,
            content={"error": "Empty message. Send JSON {'message': '...'} or plain text body."},
        )

    return handle_message(user_id, message)

@app.get("/")
def root():
    return {"status": "ok", "hint": "Use POST /chat (JSON or text) or open /docs"}