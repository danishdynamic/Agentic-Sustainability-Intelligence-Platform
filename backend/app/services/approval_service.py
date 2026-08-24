from datetime import datetime, timezone
from sqlalchemy import select
from app.db.session import session_scope
from app.models import Approval, Run


def get_pending(run_id: str) -> dict | None:
    with session_scope() as session:
        if not session.get(Run, run_id):
            return None
        item = session.scalar(
            select(Approval).where(
                Approval.run_id == run_id, Approval.status == "pending"
            )
        )
        if not item:
            item = Approval(
                id=f"approval_{run_id}",
                run_id=run_id,
                action="save_report",
                risk_level="MEDIUM",
                payload={"filename": "sustainability-report.md"},
            )
            session.add(item)
        return {
            "approval_id": item.id,
            "action": item.action,
            "risk_level": item.risk_level,
            "payload": item.payload,
            "options": ["approve", "edit", "reject"],
        }


def resolve(
    run_id: str, approval_id: str, decision: str, edited_payload: dict | None
) -> dict | None:
    with session_scope() as session:
        item = session.scalar(
            select(Approval).where(
                Approval.id == approval_id, Approval.run_id == run_id
            )
        )
        if not item:
            return None
        item.status = "approved" if decision in {"approve", "edit"} else "rejected"
        item.edited_payload = edited_payload
        item.resolved_at = datetime.now(timezone.utc)
        return {"run_id": run_id, "status": "resumed", "decision": decision}
