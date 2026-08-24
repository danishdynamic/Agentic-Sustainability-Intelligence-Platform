from fastapi import APIRouter
from app.schemas import ApprovalRequest
from app.services import approval_service

router = APIRouter(prefix="/api/v1/runs", tags=["approvals"])


@router.get("/{run_id}/approval")
def approval(run_id: str):
    return approval_service.get_pending(run_id)


@router.post("/{run_id}/approval")
def resolve(run_id: str, request: ApprovalRequest):
    return approval_service.resolve(
        run_id, request.approval_id, request.decision, request.edited_payload
    )
