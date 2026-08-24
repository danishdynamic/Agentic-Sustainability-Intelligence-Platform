from app.config.settings import get_settings
from app.rag.embeddings import embed_text
from app.rag.lexical_search import search as lexical_search
from app.rag.vector_store import search as vector_search


def search(query: str, filters: dict) -> dict:
    embedding, embedding_hit = embed_text(query)
    vector = vector_search(embedding, filters, get_settings().retrieval_top_k)
    lexical = lexical_search(query, filters, get_settings().retrieval_top_k)
    by_id = {item["chunk_id"]: item for item in vector}
    for item in lexical:
        if item["chunk_id"] in by_id:
            by_id[item["chunk_id"]]["score"] += item["score"]
            by_id[item["chunk_id"]]["retrieval"] = "hybrid"
        else:
            by_id[item["chunk_id"]] = item
    return {
        "candidates": sorted(
            by_id.values(), key=lambda item: item["score"], reverse=True
        ),
        "vector_count": len(vector),
        "lexical_count": len(lexical),
        "embedding_hit": embedding_hit,
    }
