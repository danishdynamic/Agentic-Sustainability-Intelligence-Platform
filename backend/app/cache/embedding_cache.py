from app.cache.redis_cache import cache


def get_embedding(content_hash: str) -> list[float] | None:
    return cache.get_json(f"embedding:{content_hash}")


def set_embedding(content_hash: str, embedding: list[float]) -> bool:
    return cache.set_json(f"embedding:{content_hash}", embedding)
