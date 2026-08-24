from sqlalchemy import select
from app.db.session import session_scope
from app.models import Document
from app.rag.ingestion import ingest


def ingest_document(
    path: str, category: str, topic: str, year: int, region: str
) -> dict:
    return ingest(path, category, topic, year, region)


def list_documents(filters: dict) -> list[dict]:
    with session_scope() as session:
        query = select(Document)
        for field in ("category", "topic", "year", "region"):
            if filters.get(field) is not None:
                query = query.where(getattr(Document, field) == filters[field])
        return [
            {
                "id": doc.id,
                "name": doc.name,
                "category": doc.category,
                "topic": doc.topic,
                "year": doc.year,
                "region": doc.region,
            }
            for doc in session.scalars(query).all()
        ]
