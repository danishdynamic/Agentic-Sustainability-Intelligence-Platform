from datetime import datetime, timezone

from app.cache.redis_cache import cache
from app.config.settings import get_settings


def record_gemini_usage(tokens: int = 0) -> dict:
    now = datetime.now(timezone.utc)
    minute_key = f"quota:minute:{now.strftime('%Y%m%d%H%M')}"
    day_key = f"quota:day:{now.strftime('%Y%m%d')}"
    cache.client.incr(minute_key)
    cache.client.expire(minute_key, 120)
    cache.client.incrby(f"{day_key}:tokens", tokens)
    cache.client.expire(f"{day_key}:tokens", 172800)
    cache.client.incr(day_key)
    cache.client.expire(day_key, 172800)
    settings = get_settings()
    return {
        "rpm_limit": settings.gemini_max_rpm,
        "tpm_limit": settings.gemini_max_tpm,
        "rpd_limit": settings.gemini_max_rpd,
    }
