from __future__ import annotations
from typing import Any, Dict, List

def generate_questions(jd_text: str, candidate_summary: str) -> Dict[str, Any]:
    # MVP: templated (deterministic). You can replace with LLM later.
    technical = [
        "Walk me through a recent project that matches this JD. What was your role and impact?",
        "How do you ensure data quality and reliability in your pipeline/work?",
        "Explain a tradeoff you made between speed and correctness.",
        "Describe how you would debug a failing ETL / model drift issue.",
        "What metrics would you use to evaluate success for this role?",
    ]
    behavioral = [
        "Tell me about a time you handled conflicting stakeholder requirements (STAR).",
        "Describe a time you failed or made a mistake and what you learned.",
        "Tell me about a time you influenced without authority.",
        "How do you prioritize tasks when everything is urgent?",
        "Describe a time you improved a process end-to-end.",
    ]
    rubric = [
        {"competency": "role_fit", "signals": ["relevant experience", "clear impact", "domain understanding"]},
        {"competency": "communication", "signals": ["structured answers", "clarity", "stakeholder empathy"]},
        {"competency": "technical_depth", "signals": ["correct concepts", "tradeoffs", "problem solving"]},
    ]
    return {
        "technical": technical,
        "behavioral": behavioral,
        "rubric": rubric,
        "notes": "MVP question set; upgrade to LLM-based later.",
    }

def competency_mapper(questions: Dict[str, Any]) -> Dict[str, Any]:
    mapping = []
    for q in questions.get("technical", []):
        mapping.append({"question": q, "competency": "technical_depth"})
    for q in questions.get("behavioral", []):
        mapping.append({"question": q, "competency": "communication/leadership"})
    return {"mapping": mapping}
