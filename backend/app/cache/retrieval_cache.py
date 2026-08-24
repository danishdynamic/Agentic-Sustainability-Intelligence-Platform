import json

from app.cache.redis_cache import cache


def retrieval_key(query: str, filters: dict, version: str) -> str:
    return cache.key(
        "retrieval",
        json.dumps(
            {"query": query.strip().lower(), "filters": filters, "version": version},
            sort_keys=True,
        ),
    )


def get_retrieval(key: str) -> list[dict] | None:
    return cache.get_json(key)


def set_retrieval(key: str, candidates: list[dict]) -> bool:
    return cache.set_json(key, candidates)
