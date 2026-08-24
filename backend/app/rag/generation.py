from app.config.settings import get_settings


def generate_answer(query: str, evidence: list[dict]) -> tuple[str, dict]:
    settings = get_settings()
    context = "\n\n".join(item["content"] for item in evidence)
    if settings.gemini_api_key:
        try:
            from google import genai

            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = f"Answer only from the evidence below. Cite no unsupported claims.\nQuestion: {query}\nEvidence:\n{context}"
            response = client.models.generate_content(
                model=settings.gemini_model, contents=prompt
            )
            from app.observability.metrics import record_gemini_usage

            record_gemini_usage(len(prompt.split()) + len(response.text.split()))
            return response.text[: settings.max_output_length], {
                "provider": "gemini",
                "model": settings.gemini_model,
            }
        except Exception:
            pass
    # Local fallback is intentionally extractive, never invented from an empty context.
    return (
        evidence[0]["content"].split("\n")[-1]
        if evidence
        else "I could not find enough evidence in the knowledge base to answer reliably."
    ), {"provider": "local-extractive", "model": settings.gemini_model}
