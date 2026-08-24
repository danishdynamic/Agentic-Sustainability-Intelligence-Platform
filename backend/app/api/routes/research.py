from fastapi import APIRouter
from app.schemas import ResearchRequest
from app.services import research_service

router = APIRouter(prefix="/api/v1", tags=["research"])


@router.post("/research")
def research(request: ResearchRequest) -> dict:
    return research_service.start(
        request.query, request.filters.model_dump(exclude_none=True)
    )
