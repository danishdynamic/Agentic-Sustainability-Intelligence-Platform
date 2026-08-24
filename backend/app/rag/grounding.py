import re


def evaluate(answer: str, evidence: list[dict]) -> tuple[bool, float]:
    if not answer or not evidence:
        return False, 0.0
    evidence_text = " ".join(item["content"].lower() for item in evidence)
    claims = [claim for claim in re.split(r"[.!?]", answer.lower()) if claim.strip()]
    supported = sum(
        any(token in evidence_text for token in claim.split() if len(token) > 3)
        for claim in claims
    )
    score = supported / max(len(claims), 1)
    return score >= 0.7, round(score, 2)
