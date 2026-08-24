import hashlib
import json
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.config.settings import get_settings


class RedisCache:
    def __init__(self) -> None:
        self.client = Redis.from_url(get_settings().redis_url, decode_responses=True)
        self.ttl = get_settings().cache_ttl_seconds

    def key(self, prefix: str, value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"

    def get_json(self, key: str) -> Any | None:
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except RedisError:
            return None

    def set_json(self, key: str, value: Any, ttl: int | None = None) -> bool:
        try:
            self.client.setex(key, ttl or self.ttl, json.dumps(value))
            return True
        except RedisError:
            return False

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except RedisError:
            return False


cache = RedisCache()
