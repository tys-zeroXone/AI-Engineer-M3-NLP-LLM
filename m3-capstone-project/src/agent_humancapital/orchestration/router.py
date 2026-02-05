from __future__ import annotations
from agent_humancapital.orchestration.schemas import RoutedPlan, Intent

def classify_intent(query: str) -> Intent:
    q = query.lower()

    if any(k in q for k in ["rbac", "akses", "permission", "pii", "privacy", "redact", "bias", "compliance", "risk"]):
        return "GOVERNANCE_CHECK"

    if any(k in q for k in ["interview", "questions", "pertanyaan", "assessment", "rubric", "kompetensi"]):
        return "INTERVIEW_PREP"

    if any(k in q for k in ["skill gap", "gap skill", "kesenjangan", "extract skills", "skills", "kompetensi teknis"]):
        return "SKILL_ANALYSIS"

    if any(k in q for k in ["rank", "ranking", "match", "jd", "job description", "cocok", "compare candidates", "scoring"]):
        return "RANK_AND_MATCH"

    if any(k in q for k in ["find", "search", "cari", "resume", "candidate", "kandidat", "talent"]):
        return "RETRIEVE_CANDIDATES"

    return "GENERAL_QA"

def route(query: str) -> RoutedPlan:
    intent = classify_intent(query)

    if intent == "RETRIEVE_CANDIDATES":
        workers = ["retrieval"]
    elif intent == "RANK_AND_MATCH":
        workers = ["retrieval", "ranking"]
    elif intent == "SKILL_ANALYSIS":
        workers = ["retrieval", "skill"]
    elif intent == "INTERVIEW_PREP":
        workers = ["retrieval", "interview"]
    elif intent == "GOVERNANCE_CHECK":
        workers = ["governance"]
    else:
        workers = []  # supervisor can answer directly

    return RoutedPlan(intent=intent, workers=workers, notes="rule-based routing")
