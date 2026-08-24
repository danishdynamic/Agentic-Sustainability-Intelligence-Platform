from langgraph.graph import END, START, StateGraph

from app.graph.checkpoints import checkpointer
from app.graph.nodes import (
    corrective_node,
    fan_out_retrieval,
    generate_node,
    grounding_node,
    input_guardrail,
    lexical_retrieve,
    merge_retrieval,
    output_guardrail,
    query_analysis,
    rerank_node,
    retrieve,
    supervisor,
    vector_retrieve,
)
from app.graph.routing import after_grounding
from app.graph.state import ResearchState


def build_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("supervisor", supervisor)
    graph.add_node("query_analysis", query_analysis)
    graph.add_node("retrieve", retrieve)
    graph.add_node("vector_retrieve", vector_retrieve)
    graph.add_node("lexical_retrieve", lexical_retrieve)
    graph.add_node("merge_retrieval", merge_retrieval)
    graph.add_node("reranker", rerank_node)
    graph.add_node("generation", generate_node)
    graph.add_node("grounding", grounding_node)
    graph.add_node("corrective_rag", corrective_node)
    graph.add_node("output_guardrail", output_guardrail)
    graph.add_edge(START, "input_guardrail")
    graph.add_edge("input_guardrail", "supervisor")
    graph.add_edge("supervisor", "query_analysis")
    graph.add_conditional_edges(
        "query_analysis", fan_out_retrieval, ["vector_retrieve", "lexical_retrieve"]
    )
    graph.add_edge("vector_retrieve", "merge_retrieval")
    graph.add_edge("lexical_retrieve", "merge_retrieval")
    graph.add_edge("merge_retrieval", "reranker")
    graph.add_edge("reranker", "generation")
    graph.add_edge("generation", "grounding")
    graph.add_conditional_edges(
        "grounding",
        after_grounding,
        {"corrective_rag": "corrective_rag", "output_guardrail": "output_guardrail"},
    )
    graph.add_edge("corrective_rag", "query_analysis")
    graph.add_edge("output_guardrail", END)
    return graph.compile(checkpointer=checkpointer())
