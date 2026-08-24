import re
from collections import Counter

from sqlalchemy import select

from app.db.session import session_scope
from app.models import Chunk


def search(query: str, filters: dict, top_k: int = 20) -> list[dict]:
    terms = re.findall(r"[a-z0-9]+", query.lower())
    with session_scope() as session:
        chunks = list(session.scalars(select(Chunk)))
        ranked = []
        for chunk in chunks:
            metadata = chunk.metadata_json or {}
            if (
                filters.get("category")
                and metadata.get("category") != filters["category"]
            ):
                continue
            if (
                filters.get("year_from")
                and metadata.get("year", 0) < filters["year_from"]
            ):
                continue
            if (
                filters.get("year_to")
                and metadata.get("year", 9999) > filters["year_to"]
            ):
                continue
            counts = Counter(re.findall(r"[a-z0-9]+", chunk.content.lower()))
            score = sum(counts[term] for term in terms)
            if score:
                ranked.append((score, chunk))
        return [
            _serialize(chunk, float(score))
            for score, chunk in sorted(ranked, key=lambda pair: pair[0], reverse=True)[
                :top_k
            ]
        ]


def _serialize(chunk: Chunk, score: float) -> dict:
    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "content": chunk.content,
        "metadata": chunk.metadata_json,
        "score": score,
        "retrieval": "bm25",
    }
