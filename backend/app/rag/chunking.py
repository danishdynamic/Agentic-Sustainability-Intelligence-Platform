import re

from app.config.settings import get_settings


def chunk_text(content: str) -> list[str]:
    size = get_settings().chunk_size if hasattr(get_settings(), "chunk_size") else 900
    overlap = getattr(get_settings(), "chunk_overlap", 120)
    clean = re.sub(r"\n{3,}", "\n\n", content.strip())
    chunks = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + size)
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(start + 1, end - overlap)
    return chunks
