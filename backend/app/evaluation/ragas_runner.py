from datetime import datetime, timezone
import json
from pathlib import Path

from app.evaluation.datasets import load_dataset


def run_baseline() -> dict:
    dataset = load_dataset()
    result = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "dataset_size": len(dataset),
        "metrics": {
            "faithfulness": None,
            "answer_relevance": None,
            "context_relevance": None,
            "context_recall": None,
        },
        "status": "ready_for_ragas",
    }
    output = Path(__file__).resolve().parents[3] / "evaluation" / "results"
    output.mkdir(exist_ok=True)
    (output / "latest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
