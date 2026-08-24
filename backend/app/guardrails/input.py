import re
from app.config.settings import get_settings


def validate_input(query: str) -> None:
    if len(query.strip()) > get_settings().max_input_length:
        raise ValueError("INPUT_TOO_LONG")
    if re.search(
        r"ignore (all|any|previous)|reveal (the )?system prompt|jailbreak", query, re.I
    ):
        raise ValueError("PROMPT_INJECTION")
    if re.search(r"\\b(?:\\d[ -]?){13,16}\\b|[\\w.+-]+@[\\w-]+\\.[\\w.-]+", query):
        raise ValueError("PII_DETECTED")
