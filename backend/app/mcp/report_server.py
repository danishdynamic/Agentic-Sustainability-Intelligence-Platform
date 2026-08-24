from mcp.server.fastmcp import FastMCP

mcp = FastMCP("report")


@mcp.tool()
def create_report(title: str, content: str) -> dict:
    return {"title": title, "content": content, "status": "draft"}


@mcp.tool()
def save_report(filename: str, content: str) -> dict:
    from pathlib import Path

    output = Path("reports")
    output.mkdir(exist_ok=True)
    destination = output / Path(filename).name
    destination.write_text(content, encoding="utf-8")
    return {"filename": str(destination), "status": "saved"}


if __name__ == "__main__":
    mcp.run()
