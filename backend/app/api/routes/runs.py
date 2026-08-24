from fastapi import APIRouter
from app.services import research_service

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


@router.get("/{run_id}")
def run(run_id: str):
    return research_service.get_run(run_id)


@router.get("/{run_id}/events")
def events(run_id: str):
    return {"events": research_service.get_events(run_id) or []}


@router.get("/{run_id}/result")
def result(run_id: str):
    return research_service.get_result(run_id)
