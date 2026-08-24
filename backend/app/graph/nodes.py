from langgraph.types import interrupt

from app.rag.citation import citations
from app.rag.corrective_rag import corrective_query
from app.rag.generation import generate_answer
from app.rag.grounding import evaluate
from app.rag.hybrid_search import search
from app.config.settings import get_settings
from app.rag.embeddings import embed_text
from app.rag.lexical_search import search as lexical_search
from app.rag.vector_store import search as vector_search
from app.rag.query_rewriter import rewrite_query
from app.rag.reranker import rerank
from app.guardrails.output import validate_output


def _event(
    state: dict, event_type: str, agent: str, message: str, node: str
) -> list[dict]:
    return [{"type": event_type, "agent": agent, "message": message, "node": node}]


def input_guardrail(state: dict) -> dict:
    return {
        "events": _event(
            state,
            "agent_completed",
            "input_guardrail",
            "Input accepted",
            "input_guardrail",
        )
    }


def supervisor(state: dict) -> dict:
    return {
        "events": _event(
            state,
            "agent_completed",
            "supervisor",
            "Research plan created",
            "supervisor",
        )
    }


def query_analysis(state: dict) -> dict:
    plan = rewrite_query(state["query"], state.get("filters", {}))
    return {
        "rewritten_queries": plan.queries,
        "events": _event(
            state,
            "agent_completed",
            "query_agent",
            "Structured query plan created",
            "query_analysis",
        ),
    }


def retrieve(state: dict) -> dict:
    result = search(state["rewritten_queries"][0], state.get("filters", {}))
    return {
        "retrieval_results": result["candidates"],
        "retrieval_count": len(result["candidates"]),
        "cache": {"embedding_hit": result["embedding_hit"]},
        "events": _event(
            state,
            "retrieval",
            "researcher",
            f"Vector + BM25 returned {len(result['candidates'])} candidates",
            "hybrid_retrieval",
        ),
    }


def fan_out_retrieval(state: dict):
    from langgraph.types import Send

    return [Send("vector_retrieve", state), Send("lexical_retrieve", state)]


def vector_retrieve(state: dict) -> dict:
    embedding, embedding_hit = embed_text(state["rewritten_queries"][0])
    results = vector_search(
        embedding, state.get("filters", {}), get_settings().retrieval_top_k
    )
    return {
        "retrieval_results": results,
        "cache": {"embedding_hit": embedding_hit},
        "events": _event(
            state,
            "retrieval",
            "vector_search",
            f"pgvector returned {len(results)} candidates",
            "vector_retrieval",
        ),
    }


def lexical_retrieve(state: dict) -> dict:
    results = lexical_search(
        state["rewritten_queries"][0],
        state.get("filters", {}),
        get_settings().retrieval_top_k,
    )
    return {
        "retrieval_results": results,
        "events": _event(
            state,
            "retrieval",
            "bm25_search",
            f"BM25 returned {len(results)} candidates",
            "lexical_retrieval",
        ),
    }


def merge_retrieval(state: dict) -> dict:
    deduplicated = {}
    for item in state.get("retrieval_results", []):
        existing = deduplicated.get(item["chunk_id"])
        if existing:
            existing["score"] += item.get("score", 0)
            existing["retrieval"] = "hybrid"
        else:
            deduplicated[item["chunk_id"]] = item
    merged = sorted(
        deduplicated.values(), key=lambda item: item.get("score", 0), reverse=True
    )
    return {
        "merged_results": merged,
        "retrieval_count": len(merged),
        "events": [
            {
                "type": "retrieval",
                "agent": "researcher",
                "message": f"Merged {len(merged)} unique candidates",
                "node": "hybrid_merge",
            }
        ],
    }


def rerank_node(state: dict) -> dict:
    selected = rerank(
        state["query"], state.get("merged_results", state.get("retrieval_results", []))
    )
    return {
        "reranked_results": selected,
        "evidence": selected,
        "rerank_count": len(selected),
        "selected_count": len(selected),
        "events": _event(
            state,
            "rerank",
            "researcher",
            f"Selected {len(selected)} evidence chunks",
            "reranker",
        ),
    }


def generate_node(state: dict) -> dict:
    answer, metadata = generate_answer(state["query"], state.get("evidence", []))
    return {
        "answer": answer,
        "metadata": metadata,
        "events": _event(
            state,
            "generation",
            "analyst",
            "Generated answer from selected evidence",
            "generation",
        ),
    }


def grounding_node(state: dict) -> dict:
    passed, score = evaluate(state.get("answer", ""), state.get("evidence", []))
    return {
        "grounding_passed": passed,
        "grounding_score": score,
        "citations": citations(state.get("evidence", [])),
        "events": _event(
            state,
            "grounding",
            "critic",
            f"Grounding check {'passed' if passed else 'failed'} at {score:.2f}",
            "grounding",
        ),
    }


def corrective_node(state: dict) -> dict:
    retry_count = state.get("rag_retry_count", 0) + 1
    return {
        "query": corrective_query(
            state["query"], state.get("filters", {}), retry_count
        ),
        "rag_retry_count": retry_count,
        "events": _event(
            state,
            "corrective_rag",
            "critic",
            f"Retrying with targeted evidence query {retry_count}",
            "corrective_rag",
        ),
    }


def output_guardrail(state: dict) -> dict:
    validate_output(
        state.get("answer", ""),
        state.get("citations", []),
        state.get("grounding_passed", False),
    )
    return {
        "events": _event(
            state,
            "agent_completed",
            "output_guardrail",
            "Schema, citation, and grounding checks passed",
            "output_guardrail",
        )
    }


def approval_node(state: dict) -> dict:
    payload = state.get("pending_action")
    decision = interrupt({"action": payload, "options": ["approve", "edit", "reject"]})
    return {
        "approval_result": decision,
        "events": _event(
            state, "hitl_resumed", "report_agent", "Human approval received", "approval"
        ),
    }
