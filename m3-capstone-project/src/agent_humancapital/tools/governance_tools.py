from __future__ import annotations
import re
from typing import Tuple

ALLOWED_ACTIONS = {
    "guest": {"general_qa"},
    "manager": {"general_qa", "retrieve"},
    "hr": {"general_qa", "retrieve", "skill", "rank", "interview"},
    "recruiter": {"general_qa", "retrieve", "skill", "rank", "interview"},
    "admin": {"general_qa", "retrieve", "skill", "rank", "interview", "governance"},
}

PII_PATTERNS = [
    (re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b(\+?\d[\d\s\-\(\)]{8,}\d)\b"), "[REDACTED_PHONE]"),
]

BIAS_TRIGGERS = [
    "young", "old", "age", "gender", "female", "male", "married", "single",
    "religion", "race", "ethnicity", "pregnant", "disabled",
]

def rbac_enforcer(role: str, action: str) -> Tuple[bool, str]:
    role = (role or "guest").lower()
    action = action.lower()

    allowed = ALLOWED_ACTIONS.get(role, {"general_qa"})
    if action not in allowed:
        return False, f"Access denied for role='{role}' to action='{action}'."
    return True, "OK"

def pii_redactor(text: str) -> str:
    out = text
    for pattern, repl in PII_PATTERNS:
        out = pattern.sub(repl, out)
    return out

def bias_checker(text: str) -> str:
    t = text.lower()
    hits = [w for w in BIAS_TRIGGERS if w in t]
    if hits:
        return f"Bias warning: detected potentially sensitive terms {sorted(set(hits))}."
    return "OK"

def risk_detector(text: str) -> str:
    # simple heuristic; extend later
    t = text.lower()
    if "guarantee" in t or "100%" in t:
        return "Risk: overconfident claim detected."
    return "OK"
