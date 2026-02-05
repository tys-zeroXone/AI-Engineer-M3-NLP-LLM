from __future__ import annotations
from typing import Any, Dict, List

COMMON_SKILLS = [
    "python", "sql", "excel", "power bi", "tableau", "spark", "pandas",
    "ml", "machine learning", "nlp", "aws", "azure", "gcp", "docker",
    "kubernetes", "java", "javascript", "react", "node", "postgres",
]

def extract_skills(text: str) -> Dict[str, Any]:
    t = (text or "").lower()
    found = [s for s in COMMON_SKILLS if s in t]
    return {"skills": sorted(set(found))}

def skill_gap_analysis(jd_skills: List[str], candidate_skills: List[str]) -> Dict[str, Any]:
    jd = set([s.lower() for s in jd_skills])
    cv = set([s.lower() for s in candidate_skills])
    return {
        "missing": sorted(list(jd - cv)),
        "matched": sorted(list(jd & cv)),
        "extra": sorted(list(cv - jd)),
    }

def skill_trend_aggregator(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for c in candidates:
        skills = c.get("skills", [])
        for s in skills:
            counts[s] = counts.get(s, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]
    return {"top_skills": top}
