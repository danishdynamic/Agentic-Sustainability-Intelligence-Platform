import operator
from typing import Annotated, Any, TypedDict


class ResearchState(TypedDict, total=False):
    run_id: str
    query: str
    rewritten_queries: list[str]
    filters: dict[str, Any]
    retrieval_results: Annotated[list[dict], operator.add]
    merged_results: list[dict]
    reranked_results: list[dict]
    evidence: list[dict]
    answer: str
    citations: list[dict]
    grounding_score: float
    grounding_passed: bool
    rag_retry_count: int
    pending_action: dict | None
    approval_result: dict | None
    events: Annotated[list[dict], operator.add]
    retrieval_count: int
    rerank_count: int
    selected_count: int
    cache: dict
    metadata: dict
