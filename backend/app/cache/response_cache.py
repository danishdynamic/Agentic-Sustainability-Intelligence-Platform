from app.cache.redis_cache import cache


def response_key(query: str, filters: dict, version: str, model: str) -> str:
    return cache.key("response", f"{query.strip().lower()}|{filters}|{version}|{model}")


def get_response(key: str) -> dict | None:
    return cache.get_json(key)


def set_response(key: str, result: dict) -> bool:
    return cache.set_json(key, result)
