from pathlib import Path
import json

DATASET_PATH = (
    Path(__file__).resolve().parents[3]
    / "evaluation"
    / "datasets"
    / "sustainability_questions.json"
)


def load_dataset() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))
