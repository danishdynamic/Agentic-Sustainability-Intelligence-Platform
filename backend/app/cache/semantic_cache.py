import math

from app.cache.redis_cache import cache
from app.config.settings import get_settings


def _cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    denominator = math.sqrt(sum(a * a for a in left)) * math.sqrt(
        sum(b * b for b in right)
    )
    return numerator / denominator if denominator else 0.0


def find_similar(
    embedding: list[float], filters: dict, version: str, model: str
) -> dict | None:
    # Redis stores a bounded query index; filter and model/version remain part of the cache namespace.
    items = (
        cache.get_json(cache.key("semantic-index", f"{filters}|{version}|{model}"))
        or []
    )
    threshold = get_settings().semantic_cache_threshold
    best = max(
        ((_cosine(embedding, item["embedding"]), item) for item in items),
        default=(0, None),
        key=lambda pair: pair[0],
    )
    return best[1]["result"] if best[1] and best[0] >= threshold else None


def store(
    embedding: list[float], filters: dict, version: str, model: str, result: dict
) -> bool:
    key = cache.key("semantic-index", f"{filters}|{version}|{model}")
    items = cache.get_json(key) or []
    items.append({"embedding": embedding, "result": result})
    return cache.set_json(key, items[-100:])
