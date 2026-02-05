from __future__ import annotations
from typing import Any, Dict, List
from agent_humancapital.tools.retrieval_tools import semantic_search, keyword_search, metadata_filter
from agent_humancapital.tools.ranking_tools import ranking_candidates, explain_score
from agent_humancapital.tools.skill_tools import extract_skills, skill_gap_analysis, skill_trend_aggregator
from agent_humancapital.tools.interview_tools import generate_questions, competency_mapper

def run_retrieval_worker(query: str, k: int, category: str | None = None) -> Dict[str, Any]:
    base = semantic_search(query, k=k)
    results = base["results"]

    if category:
        results = metadata_filter(results, category=category)["results"]

    # optional additional pass: keyword filter for tight constraints
    kw = keyword_search(query, results, k=k)
    # fallback: if keyword filter returns nothing, keep semantic
    final = kw["results"] if kw["results"] else results[:k]

    return {"candidates": final, "debug": {"semantic": base, "keyword": kw, "category": category}}

def run_ranking_worker(candidates: List[Dict[str, Any]], jd_text: str) -> Dict[str, Any]:
    ranked = ranking_candidates(candidates, jd_text)["ranked"]
    explanations = [explain_score(c) for c in ranked[:10]]
    return {"ranked": ranked, "explanations": explanations}

def run_skill_worker(candidates: List[Dict[str, Any]], jd_skills: List[str] | None = None) -> Dict[str, Any]:
    enriched = []
    for c in candidates:
        skills = extract_skills(c.get("preview", ""))["skills"]
        enriched.append({**c, "skills": skills})

    trend = skill_trend_aggregator(enriched)
    out: Dict[str, Any] = {"candidates": enriched, "trend": trend}

    if jd_skills:
        gaps = []
        for c in enriched[:10]:
            gap = skill_gap_analysis(jd_skills, c.get("skills", []))
            gaps.append({"id": c.get("id"), **gap})
        out["gaps"] = gaps

    return out

def run_interview_worker(jd_text: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
    qs = generate_questions(jd_text, candidate_summary=candidate.get("preview", ""))
    mapping = competency_mapper(qs)
    return {"questions": qs, "competency_map": mapping}
