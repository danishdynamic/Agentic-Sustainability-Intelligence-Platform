from app.config.settings import get_settings


def after_grounding(state: dict) -> str:
    if state.get("grounding_passed"):
        return "output_guardrail"
    if state.get("rag_retry_count", 0) < get_settings().max_rag_retries:
        return "corrective_rag"
    return "output_guardrail"
