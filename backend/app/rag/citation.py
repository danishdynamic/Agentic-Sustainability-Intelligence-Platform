def citations(evidence: list[dict]) -> list[dict]:
    return [
        {
            "document_id": item["document_id"],
            "document_name": item["metadata"].get(
                "source_name", f"document-{item['document_id']}.md"
            ),
            "chunk_id": item["chunk_id"],
            "section": item["metadata"].get("section", "Knowledge base"),
            "text": item["content"],
            "relevance_score": item.get("rerank_score", item.get("score", 0)),
        }
        for item in evidence
    ]
