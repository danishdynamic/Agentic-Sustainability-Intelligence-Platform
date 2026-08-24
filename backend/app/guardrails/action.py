from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


def risk_for(action: str) -> RiskLevel:
    if action in {"read", "search"}:
        return RiskLevel.LOW
    if action in {"create_report", "save_report"}:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH
