from app.rag.query_rewriter import rewrite_query


def corrective_query(query: str, filters: dict, retry_count: int) -> str:
    plan = rewrite_query(query, filters)
    return f"{plan.queries[min(retry_count, len(plan.queries) - 1)]} verified target evidence"
