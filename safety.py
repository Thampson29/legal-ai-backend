import re

ILLEGAL = [
    r"\bforge\b",
    r"\bfake\b.*\b(doc|document|evidence)\b",
    r"\bbribe\b",
    r"\bblackmail\b",
    r"\bextort\b",
    r"\bthreaten\b",
]

EMERGENCY = [
    r"\bviolence\b",
    r"\bassault\b",
    r"\brape\b",
    r"\bstalking\b",
    r"\bkill myself\b",
    r"\bsuicide\b",
]

def classify(text: str) -> str:
    t = (text or "").lower()
    if any(re.search(p, t) for p in EMERGENCY):
        return "emergency"
    if any(re.search(p, t) for p in ILLEGAL):
        return "illegal"
    return "ok"

def canned_response(label: str) -> str:
    if label == "illegal":
        return (
            "I can’t help with anything illegal or harmful.\n"
            "This is general information, not legal advice.\n"
            "If you explain what happened, I can suggest lawful options (reporting channels, evidence preservation, and next steps)."
        )
    if label == "emergency":
        return (
            "If you are in immediate danger, contact emergency services now.\n"
            "In India you can call 112.\n"
            "This is general information, not legal advice."
        )
    return ""