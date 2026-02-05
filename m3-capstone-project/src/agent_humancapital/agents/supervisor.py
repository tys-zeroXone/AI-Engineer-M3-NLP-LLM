from __future__ import annotations
from typing import Any, Dict, List, Optional
from agent_humancapital.orchestration.router import route
from agent_humancapital.orchestration.schemas import SupervisorInput, WorkerResult
from agent_humancapital.config import SETTINGS
from agent_humancapital.tools.governance_tools import rbac_enforcer, pii_redactor, bias_checker, risk_detector
from agent_humancapital.agents.workers import (
    run_retrieval_worker,
    run_ranking_worker,
    run_skill_worker,
    run_interview_worker,
)

def supervisor_run(payload: SupervisorInput) -> Dict[str, Any]:
    query = payload.query
    role = payload.user.role or "guest"

    plan = route(query)
    tool_traces: List[Dict[str, Any]] = []
    worker_results: List[WorkerResult] = []

    # If no workers, answer directly (MVP)
    if not plan.workers:
        answer = f"I can help with resume search, ranking, skill analysis, interview prep, and governance checks. Your query: {query}"
        safe = _govern_and_finalize(answer, role, tool_traces)
        return safe

    # RBAC gating based on intent/workers
    required_action = _action_from_workers(plan.workers)
    ok, msg = rbac_enforcer(role, required_action)
    tool_traces.append({"tool": "rbac_enforcer", "input": {"role": role, "action": required_action}, "output": {"ok": ok, "msg": msg}})
    if not ok:
        return _govern_and_finalize(msg, role, tool_traces)

    # 1) Retrieval is foundational for most flows
    candidates: List[Dict[str, Any]] = []
    if "retrieval" in plan.workers:
        retr = run_retrieval_worker(query=query, k=SETTINGS.TOP_K_DEFAULT)
        tool_traces.append({"worker": "retrieval", "output": retr.get("debug", {})})
        candidates = retr["candidates"]
        worker_results.append(WorkerResult(worker="retrieval", content=_format_candidates(candidates), raw=retr))

    # 2) Ranking
    if "ranking" in plan.workers:
        jd_text = _extract_jd_text(query)
        ranked = run_ranking_worker(candidates=candidates, jd_text=jd_text)
        tool_traces.append({"worker": "ranking", "output": {"explanations": ranked.get("explanations", [])}})
        worker_results.append(WorkerResult(worker="ranking", content=_format_ranked(ranked["ranked"]), raw=ranked))
        candidates = ranked["ranked"]  # update downstream ordering

    # 3) Skill analysis
    if "skill" in plan.workers:
        jd_skills = _extract_jd_skills(query)
        skills = run_skill_worker(candidates=candidates, jd_skills=jd_skills)
        tool_traces.append({"worker": "skill", "output": {"trend": skills.get("trend", {})}})
        worker_results.append(WorkerResult(worker="skill", content=_format_skills(skills), raw=skills))

    # 4) Interview prep
    if "interview" in plan.workers:
        jd_text = _extract_jd_text(query)
        target = candidates[0] if candidates else {"id": None, "preview": ""}
        interview = run_interview_worker(jd_text=jd_text, candidate=target)
        tool_traces.append({"worker": "interview", "output": {"rubric": interview["questions"].get("rubric", [])}})
        worker_results.append(WorkerResult(worker="interview", content=_format_interview(interview), raw=interview))

    # Merge results
    answer = _merge(worker_results, plan.intent)
    return _govern_and_finalize(answer, role, tool_traces)

def _govern_and_finalize(text: str, role: str, tool_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    redacted = pii_redactor(text)
    bias = bias_checker(redacted)
    risk = risk_detector(redacted)

    tool_traces.append({"tool": "pii_redactor", "output": "applied"})
    tool_traces.append({"tool": "bias_checker", "output": bias})
    tool_traces.append({"tool": "risk_detector", "output": risk})

    return {
        "answer": redacted,
        "governance": {"bias": bias, "risk": risk, "role": role},
        "tool_traces": tool_traces,
    }

def _action_from_workers(workers: List[str]) -> str:
    if "governance" in workers:
        return "governance"
    if "interview" in workers:
        return "interview"
    if "skill" in workers:
        return "skill"
    if "ranking" in workers:
        return "rank"
    if "retrieval" in workers:
        return "retrieve"
    return "general_qa"

def _merge(results: List[WorkerResult], intent: str) -> str:
    parts = [f"**Intent:** {intent}"]
    for r in results:
        parts.append(f"\n### {r.worker.upper()} RESULT\n{r.content}")
    parts.append("\n### Next actions\n- Refine by adding role/title, years of experience, location, or specific skills.\n- Paste JD text for more accurate matching.")
    return "\n".join(parts)

def _format_candidates(cands: List[Dict[str, Any]]) -> str:
    if not cands:
        return "No candidates found."
    lines = []
    for i, c in enumerate(cands, 1):
        lines.append(
            f"{i}. ID={c.get('id')} | category={c.get('category')} | score={c.get('score'):.3f}\n"
            f"   preview: {c.get('preview','')[:250]}..."
        )
    return "\n".join(lines)

def _format_ranked(ranked: List[Dict[str, Any]]) -> str:
    if not ranked:
        return "No ranked candidates."
    lines = []
    for i, c in enumerate(ranked[:10], 1):
        lines.append(
            f"{i}. ID={c.get('id')} | combined={c.get('combined_score'):.3f} | jd_match={c.get('jd_match_score'):.3f} | semantic={c.get('score'):.3f}\n"
            f"   matched_terms: {c.get('matched_terms', [])}"
        )
    return "\n".join(lines)

def _format_skills(sk: Dict[str, Any]) -> str:
    cands = sk.get("candidates", [])
    trend = sk.get("trend", {}).get("top_skills", [])
    gaps = sk.get("gaps", [])

    out = []
    if cands:
        out.append("Top candidates skill snapshots:")
        for c in cands[:5]:
            out.append(f"- ID={c.get('id')}: {c.get('skills', [])}")
    if trend:
        out.append("\nSkill trends (top 10):")
        out.extend([f"- {s}: {n}" for s, n in trend[:10]])
    if gaps:
        out.append("\nSkill gaps vs JD skills (top 5 candidates):")
        for g in gaps[:5]:
            out.append(f"- ID={g.get('id')}: missing={g.get('missing', [])}, matched={g.get('matched', [])}")
    return "\n".join(out) if out else "No skill analysis output."

def _format_interview(inter: Dict[str, Any]) -> str:
    qs = inter.get("questions", {})
    tech = qs.get("technical", [])
    beh = qs.get("behavioral", [])
    rubric = qs.get("rubric", [])
    out = ["Interview Questions:"]
    out.append("\nTechnical:")
    out.extend([f"- {q}" for q in tech])
    out.append("\nBehavioral:")
    out.extend([f"- {q}" for q in beh])
    out.append("\nRubric:")
    out.extend([f"- {r}" for r in rubric])
    return "\n".join(out)

def _extract_jd_text(query: str) -> str:
    # MVP heuristic: if user pasted "JD:" use that
    lower = query.lower()
    if "jd:" in lower:
        return query.split("JD:", 1)[1].strip()
    return query

def _extract_jd_skills(query: str) -> Optional[List[str]]:
    # MVP: allow "skills: python, sql, ..." pattern
    lower = query.lower()
    if "skills:" in lower:
        tail = query.split("skills:", 1)[1]
        items = [s.strip() for s in tail.split(",") if s.strip()]
        return items or None
    return None
