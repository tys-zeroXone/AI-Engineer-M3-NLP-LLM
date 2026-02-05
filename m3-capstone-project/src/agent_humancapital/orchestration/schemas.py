from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

Intent = Literal[
    "RETRIEVE_CANDIDATES",
    "RANK_AND_MATCH",
    "SKILL_ANALYSIS",
    "INTERVIEW_PREP",
    "GOVERNANCE_CHECK",
    "GENERAL_QA",
]

class UserContext(BaseModel):
    user_id: str = Field(default="anonymous")
    role: str = Field(default="guest")  # guest/hr/recruiter/manager/admin


class SupervisorInput(BaseModel):
    query: str
    history: str = ""
    user: UserContext
    top_k: int = 5  # NEW: UI can control top-k results


class RoutedPlan(BaseModel):
    intent: Intent
    workers: List[str]
    notes: str = ""

class WorkerResult(BaseModel):
    worker: str
    content: str
    raw: Dict[str, Any] = {}
