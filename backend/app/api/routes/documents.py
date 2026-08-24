from fastapi import APIRouter
from app.schemas import IngestRequest
from app.services import document_service

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("")
def documents():
    return {"documents": document_service.list_documents({})}


@router.post("/ingest")
def ingest(request: IngestRequest):
    return document_service.ingest_document(
        request.path, request.category, request.topic, request.year, request.region
    )
