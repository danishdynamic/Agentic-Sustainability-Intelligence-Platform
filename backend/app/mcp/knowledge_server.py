from mcp.server.fastmcp import FastMCP

mcp = FastMCP("knowledge")


@mcp.tool()
def search_knowledge(
    query: str, category: str | None = None, year: int | None = None
) -> dict:
    from app.rag.lexical_search import search

    return {"results": search(query, {"category": category, "year": year}, 20)}


@mcp.tool()
def get_document(document_id: str) -> dict:
    from sqlalchemy import select
    from app.db.session import session_scope
    from app.models import Document

    with session_scope() as session:
        item = session.get(Document, document_id)
        return (
            {"id": item.id, "name": item.name, "path": item.path}
            if item
            else {"error": "DOCUMENT_NOT_FOUND"}
        )


@mcp.tool()
def list_documents(category: str | None = None) -> dict:
    from app.services.document_service import list_documents as list_indexed

    return {"documents": list_indexed({"category": category})}


if __name__ == "__main__":
    mcp.run()
