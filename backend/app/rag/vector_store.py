from sqlalchemy import select

from app.db.session import session_scope
from app.models import Chunk


def search(embedding: list[float], filters: dict, top_k: int = 20) -> list[dict]:
    # pgvector cosine distance performs the production query inside PostgreSQL.
    with session_scope() as session:
        query = (
            select(Chunk)
            .order_by(Chunk.embedding.cosine_distance(embedding))
            .limit(top_k)
        )
        chunks = list(session.scalars(query))
        return [
            _serialize(chunk, 1.0 - (index / max(len(chunks), 1)))
            for index, chunk in enumerate(chunks)
            if _matches(chunk, filters)
        ]


def _matches(chunk: Chunk, filters: dict) -> bool:
    metadata = chunk.metadata_json or {}
    return not (
        (filters.get("category") and metadata.get("category") != filters["category"])
        or (filters.get("year_from") and metadata.get("year", 0) < filters["year_from"])
        or (filters.get("year_to") and metadata.get("year", 9999) > filters["year_to"])
    )


def _serialize(chunk: Chunk, score: float) -> dict:
    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "content": chunk.content,
        "metadata": chunk.metadata_json,
        "score": score,
        "retrieval": "vector",
    }
