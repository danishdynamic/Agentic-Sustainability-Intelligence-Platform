import re

from app.config.settings import get_settings


def rerank(query: str, candidates: list[dict]) -> list[dict]:
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    scored = []
    for candidate in candidates:
        words = set(re.findall(r"[a-z0-9]+", candidate["content"].lower()))
        overlap = len(terms & words) / max(len(terms), 1)
        candidate = {
            **candidate,
            "rerank_score": round(candidate["score"] + overlap, 4),
        }
        scored.append(candidate)
    return sorted(scored, key=lambda item: item["rerank_score"], reverse=True)[
        : get_settings().rerank_top_k
    ]
