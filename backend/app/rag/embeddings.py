import hashlib
import math

from app.cache.embedding_cache import get_embedding, set_embedding
from app.config.settings import get_settings


def _local_embedding(text: str) -> list[float]:
    dimensions = get_settings().embedding_dimensions
    values = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).digest()
        for offset in range(0, min(len(digest), 24), 3):
            index = int.from_bytes(digest[offset : offset + 2], "big") % dimensions
            values[index] += (digest[offset + 2] / 255) or 0.01
    norm = math.sqrt(sum(value * value for value in values)) or 1
    return [value / norm for value in values]


def embed_text(text: str) -> tuple[list[float], bool]:
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cached = get_embedding(content_hash)
    if cached:
        return cached, True
    settings = get_settings()
    embedding = _local_embedding(text)
    if settings.gemini_api_key:
        try:
            from google import genai

            client = genai.Client(api_key=settings.gemini_api_key)
            response = client.models.embed_content(
                model=settings.gemini_embedding_model, contents=text
            )
            embedding = list(response.embeddings[0].values)
        except Exception:
            # Keep ingestion available when Gemini is temporarily unavailable.
            embedding = _local_embedding(text)
    set_embedding(content_hash, embedding)
    return embedding, False
