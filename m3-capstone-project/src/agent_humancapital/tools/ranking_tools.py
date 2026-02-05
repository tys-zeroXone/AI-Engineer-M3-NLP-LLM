from __future__ import annotations
from typing import Any, Dict, List
import math

def jd_matcher(jd_text: str, candidate_preview: str) -> Dict[str, Any]:
    # MVP heuristic: token overlap
    jd_tokens = set([t for t in _tokens(jd_text) if len(t) > 2])
    cv_tokens = set([t for t in _tokens(candidate_preview) if len(t) > 2])

    if not jd_tokens:
        score = 0.0
    else:
        score = len(jd_tokens & cv_tokens) / max(1, len(jd_tokens))
    return {
        "score": float(score),
        "matched_terms": sorted(list(jd_tokens & cv_tokens))[:30],
    }

def ranking_candidates(candidates: List[Dict[str, Any]], jd_text: str) -> Dict[str, Any]:
    ranked = []
    for c in candidates:
        match = jd_matcher(jd_text, c.get("preview", ""))
        combined = _combine_scores(c.get("score", 0.0), match["score"])
        ranked.append({
            **c,
            "jd_match_score": match["score"],
            "combined_score": combined,
            "matched_terms": match["matched_terms"],
        })

    ranked.sort(key=lambda x: x["combined_score"], reverse=True)
    return {"ranked": ranked}

def explain_score(candidate: Dict[str, Any]) -> str:
    return (
        f"Candidate {candidate.get('id')} | "
        f"semantic={candidate.get('score'):.3f}, "
        f"jd_match={candidate.get('jd_match_score'):.3f}, "
        f"combined={candidate.get('combined_score'):.3f}. "
        f"Matched terms: {candidate.get('matched_terms', [])}"
    )

def _tokens(s: str) -> List[str]:
    return [t.strip(".,:;()[]{}<>\"'").lower() for t in (s or "").split()]

def _combine_scores(semantic: float, jd_match: float) -> float:
    # normalize typical distance-ish values; keep simple
    sem = float(semantic)
    jm = float(jd_match)
    # if semantic score is distance-like (smaller better) you may invert; here assume bigger better
    return 0.6 * sem + 0.4 * jm
