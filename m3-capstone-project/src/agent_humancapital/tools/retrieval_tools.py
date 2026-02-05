from __future__ import annotations
from typing import Any, Dict, List, Optional
from agent_humancapital.vectorstore import get_vectorstore
from agent_humancapital.config import SETTINGS

def semantic_search(query: str, k: int | None = None) -> Dict[str, Any]:
    vs = get_vectorstore()
    k = k or SETTINGS.TOP_K_DEFAULT

    hits = vs.similarity_search_with_score(query, k=k)
    results: List[Dict[str, Any]] = []
    for doc, score in hits:
        results.append({
            "id": doc.metadata.get("row_index"),
            "category": doc.metadata.get("category"),
            "score": float(score),
            "preview": doc.page_content[:400],
            "metadata": doc.metadata,
        })

    return {"query": query, "k": k, "results": results}

def keyword_search(query: str, resumes: List[Dict[str, Any]], k: int | None = None) -> Dict[str, Any]:
    k = k or SETTINGS.TOP_K_DEFAULT
    q = query.lower()
    filtered = [r for r in resumes if q in (r.get("preview", "").lower())]
    return {"query": query, "k": k, "results": filtered[:k], "mode": "keyword_filter_on_preview"}

def metadata_filter(resumes: List[Dict[str, Any]], category: Optional[str] = None) -> Dict[str, Any]:
    if not category:
        return {"results": resumes, "filter": "none"}

    cat = category.lower()
    filtered = [r for r in resumes if str(r.get("category", "")).lower() == cat]
    return {"results": filtered, "filter": {"category": category}}
