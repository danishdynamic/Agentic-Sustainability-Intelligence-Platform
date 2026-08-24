from app.config.settings import get_settings


def validate_output(answer: str, citations: list[dict], grounded: bool) -> None:
    if len(answer) > get_settings().max_output_length:
        raise ValueError("OUTPUT_TOO_LONG")
    if not grounded or not citations:
        raise ValueError("GROUNDING_FAILED")
