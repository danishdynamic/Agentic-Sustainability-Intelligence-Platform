from typing import Any, Literal
from pydantic import BaseModel, Field


class ResearchFilters(BaseModel):
    category: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    region: str | None = None


class ResearchOptions(BaseModel):
    use_rag: bool = True
    use_reranker: bool = True
    use_citations: bool = True
    use_cache: bool = True


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    filters: ResearchFilters = ResearchFilters()
    options: ResearchOptions = ResearchOptions()


class IngestRequest(BaseModel):
    path: str
    category: str
    topic: str
    year: int
    region: str = "global"


class ApprovalRequest(BaseModel):
    approval_id: str
    decision: Literal["approve", "edit", "reject"]
    edited_payload: dict[str, Any] | None = None
