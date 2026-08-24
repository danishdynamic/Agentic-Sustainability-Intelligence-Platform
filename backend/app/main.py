from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.db.session import init_db
from app.guardrails.input import validate_input
from app.observability.tracing import configure_tracing
from app.schemas import ApprovalRequest, IngestRequest, ResearchRequest
from app.services import approval_service, document_service, research_service

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_db()
        from app.rag.ingestion import ingest_knowledge_base

        ingest_knowledge_base()
    except Exception:
        pass
    yield


app = FastAPI(
    title="Sustainability Intelligence API", version="1.0.0", lifespan=lifespan
)
configure_tracing(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/v1/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "sustainability-api",
        "environment": settings.app_env,
    }


@app.post("/api/v1/research")
def start_research(request: ResearchRequest) -> dict:
    try:
        validate_input(request.query)
        return research_service.start(
            request.query.strip(),
            request.filters.model_dump(exclude_none=True),
            use_cache=request.options.use_cache,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail={"code": "INPUT_GUARDRAIL_FAILED", "message": str(error)},
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "RESEARCH_FAILED",
                "message": "Research infrastructure is unavailable",
            },
        ) from error


@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str) -> dict:
    result = research_service.get_run(run_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"code": "RUN_NOT_FOUND", "message": "Run does not exist"},
        )
    return result


@app.get("/api/v1/runs/{run_id}/events")
def get_events(run_id: str) -> dict:
    result = research_service.get_events(run_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "RUN_NOT_FOUND", "message": "Run does not exist"},
        )
    return {"events": result}


@app.get("/api/v1/runs/{run_id}/result")
def get_result(run_id: str) -> dict:
    result = research_service.get_result(run_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "RUN_NOT_FOUND", "message": "Run does not exist"},
        )
    return result


@app.get("/api/v1/documents")
def list_documents(
    category: str | None = None,
    topic: str | None = None,
    year: int | None = None,
    region: str | None = None,
) -> dict:
    try:
        return {
            "documents": document_service.list_documents(
                {"category": category, "topic": topic, "year": year, "region": region}
            )
        }
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DOCUMENTS_UNAVAILABLE",
                "message": "Document storage is unavailable",
            },
        ) from error


@app.post("/api/v1/documents/ingest")
def ingest_document(request: IngestRequest) -> dict:
    try:
        return document_service.ingest_document(
            request.path, request.category, request.topic, request.year, request.region
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": str(error)},
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=422,
            detail={"code": "INGESTION_FAILED", "message": "Document ingestion failed"},
        ) from error


@app.get("/api/v1/runs/{run_id}/approval")
def get_approval(run_id: str) -> dict:
    result = approval_service.get_pending(run_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"code": "RUN_NOT_FOUND", "message": "Run does not exist"},
        )
    return result


@app.post("/api/v1/runs/{run_id}/approval")
def resolve_approval(run_id: str, request: ApprovalRequest) -> dict:
    result = approval_service.resolve(
        run_id, request.approval_id, request.decision, request.edited_payload
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"code": "APPROVAL_NOT_FOUND", "message": "Approval does not exist"},
        )
    return result
