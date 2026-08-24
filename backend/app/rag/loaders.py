from pathlib import Path


def load_text(path: Path) -> str:
    if path.suffix.lower() not in {".md", ".txt"}:
        raise ValueError("Only Markdown and text documents are supported")
    return path.read_text(encoding="utf-8")
