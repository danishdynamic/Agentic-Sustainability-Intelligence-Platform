from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from app.cache.response_cache import get_response, response_key, set_response
from app.cache.semantic_cache import find_similar, store
from app.db.session import session_scope
from app.graph.state import ResearchState
from app.graph.workflow import build_research_graph
from app.models import Event, Run
from app.rag.embeddings import embed_text


def _now():
    return datetime.now(timezone.utc)


def start(query: str, filters: dict, use_cache: bool = True) -> dict:
    run_id = f"run_{uuid4().hex[:12]}"
    state: ResearchState = {
        "run_id": run_id,
        "query": query,
        "filters": filters,
        "rag_retry_count": 0,
        "events": [],
    }
    query_embedding, embedding_hit = embed_text(query)
    cache_version = "knowledge-v1"
    cached = None
    if use_cache:
        cached = get_response(
            response_key(query, filters, cache_version, "gemini-3.1-flash-lite")
        )
        if not cached:
            cached = find_similar(
                query_embedding, filters, cache_version, "gemini-3.1-flash-lite"
            )
    with session_scope() as session:
        session.add(
            Run(
                id=run_id,
                query=query,
                status="running",
                current_node="input_guardrail",
                state_json=dict(state),
            )
        )
    if cached:
        cached["cache"] = {
            **cached.get("cache", {}),
            "semantic_hit": True,
            "response_hit": True,
            "embedding_hit": embedding_hit,
        }
        with session_scope() as session:
            run = session.get(Run, run_id)
            run.status = "completed"
            run.current_node = "output_guardrail"
            run.result_json = cached
            run.completed_at = _now()
            session.add(
                Event(
                    run_id=run_id,
                    event_type="cache_hit",
                    agent="cache",
                    node="semantic_cache",
                    message="Returned a validated cached result; no agent execution required",
                )
            )
        return {"run_id": run_id, "status": "queued"}
    graph = build_research_graph()
    final = graph.invoke(state, config={"configurable": {"thread_id": run_id}})
    result = {
        "answer": final.get("answer", ""),
        "citations": final.get("citations", []),
        "retrieval": {
            "vector_count": final.get("retrieval_count", 0),
            "lexical_count": final.get("retrieval_count", 0),
            "reranked_count": final.get("rerank_count", 0),
            "selected_count": final.get("selected_count", 0),
        },
        "grounding": {
            "passed": final.get("grounding_passed", False),
            "status": "passed" if final.get("grounding_passed") else "failed",
            "score": final.get("grounding_score", 0),
        },
        "cache": {
            "semantic_hit": False,
            "embedding_hit": final.get("cache", {}).get("embedding_hit", embedding_hit),
            "retrieval_hit": False,
            "response_hit": False,
        },
        "metadata": {
            **final.get("metadata", {}),
            "rag_retries": final.get("rag_retry_count", 0),
        },
    }
    set_response(
        response_key(query, filters, cache_version, "gemini-3.1-flash-lite"), result
    )
    store(query_embedding, filters, cache_version, "gemini-3.1-flash-lite", result)
    with session_scope() as session:
        run = session.get(Run, run_id)
        run.status = "completed"
        run.current_node = "output_guardrail"
        run.result_json = result
        run.state_json = dict(final)
        run.completed_at = _now()
        session.add_all(
            [
                Event(
                    run_id=run_id,
                    event_type=item["type"],
                    agent=item["agent"],
                    node=item.get("node"),
                    message=item["message"],
                )
                for item in final.get("events", [])
            ]
        )
    return {"run_id": run_id, "status": "queued"}


def get_run(run_id: str) -> dict | None:
    with session_scope() as session:
        run = session.get(Run, run_id)
        if not run:
            return None
        total = 7
        return {
            "run_id": run.id,
            "query": run.query,
            "status": run.status,
            "current_node": run.current_node,
            "progress": {
                "completed": total if run.status == "completed" else 1,
                "total": total,
            },
            "created_at": run.created_at.isoformat(),
        }


def get_events(run_id: str) -> list[dict] | None:
    with session_scope() as session:
        if not session.get(Run, run_id):
            return None
        return [
            {
                "timestamp": item.timestamp.isoformat(),
                "type": item.event_type,
                "agent": item.agent,
                "node": item.node,
                "message": item.message,
            }
            for item in session.scalars(
                select(Event).where(Event.run_id == run_id).order_by(Event.timestamp)
            ).all()
        ]


def get_result(run_id: str) -> dict | None:
    with session_scope() as session:
        run = session.get(Run, run_id)
        return run.result_json if run else None
