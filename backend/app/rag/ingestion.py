import hashlib
import re
from pathlib import Path

from sqlalchemy import select

from app.cache.embedding_cache import get_embedding
from app.config.settings import get_settings
from app.db.session import session_scope
from app.models import Chunk, Document
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_text
from app.rag.loaders import load_text


def _project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / get_settings().knowledge_path).is_dir():
            return parent
    return Path(__file__).resolve().parents[3]


def ingest(
    path: str, category: str, topic: str, year: int, region: str = "global"
) -> dict:
    root = _project_root()
    file_path = (root / path).resolve()
    if not file_path.is_relative_to(root) or not file_path.exists():
        raise FileNotFoundError(
            "Document path is outside the knowledge base or does not exist"
        )
    content = load_text(file_path)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    with session_scope() as session:
        existing = session.scalar(
            select(Document).where(Document.path == str(file_path.relative_to(root)))
        )
        if existing and existing.content_hash == content_hash:
            existing.category = category
            existing.topic = topic
            existing.year = year
            existing.region = region
            for chunk in existing.chunks:
                chunk.metadata_json = {
                    **(chunk.metadata_json or {}),
                    "category": category,
                    "topic": topic,
                    "year": year,
                    "region": region,
                    "source_name": file_path.name,
                }
            return {
                "document_id": existing.id,
                "status": "already_indexed",
                "chunks_created": len(existing.chunks),
            }
        if existing:
            existing.content_hash = content_hash
            existing.category = category
            existing.topic = topic
            existing.year = year
            existing.region = region
            existing.chunks.clear()
            document = existing
        else:
            document = Document(
                name=file_path.name,
                path=str(file_path.relative_to(root)),
                content_hash=content_hash,
                category=category,
                topic=topic,
                year=year,
                region=region,
            )
            session.add(document)
            session.flush()
        for index, content_chunk in enumerate(chunk_text(content)):
            embedding, _ = embed_text(content_chunk)
            session.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content_chunk,
                    embedding=embedding,
                    metadata_json={
                        "category": category,
                        "topic": topic,
                        "year": year,
                        "region": region,
                        "source_name": file_path.name,
                    },
                )
            )
        return {
            "document_id": document.id,
            "status": "indexed",
            "chunks_created": len(chunk_text(content)),
        }


def ingest_knowledge_base() -> int:
    root = _project_root() / get_settings().knowledge_path
    count = 0
    for path in root.rglob("*"):
        if path.suffix.lower() in {".md", ".txt"}:
            parts = path.parts
            category = next(
                (
                    part
                    for part in (
                        "climate",
                        "emissions",
                        "energy",
                        "water",
                        "waste",
                        "sustainability",
                        "supply-chain",
                    )
                    if part in parts
                ),
                "sustainability",
            )
            year_match = re.search(r"(?:19|20)\d{2}", path.stem)
            year = int(year_match.group()) if year_match else 2026
            ingest(str(path.relative_to(root.parent)), category, path.stem, year)
            count += 1
    return count
