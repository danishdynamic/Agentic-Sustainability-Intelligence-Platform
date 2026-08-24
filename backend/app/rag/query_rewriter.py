from pydantic import BaseModel


class QueryPlan(BaseModel):
    original_query: str
    queries: list[str]
    filters: dict


def rewrite_query(query: str, filters: dict) -> QueryPlan:
    years = (
        [
            str(year)
            for year in range(
                filters.get("year_from", 2024), filters.get("year_to", 2026) + 1
            )
        ]
        if filters.get("year_from") or filters.get("year_to")
        else []
    )
    queries = [query.strip()] + [f"{query.strip()} {year}" for year in years]
    return QueryPlan(
        original_query=query, queries=list(dict.fromkeys(queries)), filters=filters
    )
