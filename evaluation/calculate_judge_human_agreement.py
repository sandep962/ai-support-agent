"""Calculate ordinal agreement after human scores are entered."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HUMAN_PATH = PROJECT_ROOT / "evaluation" / "human_reply_evaluation.csv"
JUDGE_PATH = PROJECT_ROOT / "results" / "reply_judge_scores.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "judge_human_agreement.json"
SCORE_FIELDS = ("relevance", "groundedness", "tone", "overall")
HUMAN_FIELDS = tuple(f"human_{field}" for field in SCORE_FIELDS)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    human_rows = read_csv(HUMAN_PATH)
    if len(human_rows) != 40:
        raise ValueError(f"Expected exactly 40 human-review rows, found {len(human_rows)}")
    missing = [
        row["example_id"] + ":" + row["system"]
        for row in human_rows
        if any(not row.get(field, "").strip() for field in HUMAN_FIELDS)
    ]
    if missing:
        raise ValueError(f"All 40 rows must have human scores before calculation; missing: {missing[:5]}")

    judge_rows = read_csv(JUDGE_PATH)
    judge_by_key = {(row["example_id"], row["system"]): row for row in judge_rows}
    joined = []
    for row in human_rows:
        key = (row["example_id"], row["system"])
        if key not in judge_by_key:
            raise ValueError(f"No judge score for {key}")
        joined.append((row, judge_by_key[key]))

    metrics = {}
    for field, human_field in zip(SCORE_FIELDS, HUMAN_FIELDS):
        human = [int(human_row[human_field]) for human_row, _ in joined]
        judge = [int(judge_row[field]) for _, judge_row in joined]
        if any(score < 1 or score > 5 for score in human + judge):
            raise ValueError(f"Scores for {field} must be integers from 1 through 5")
        metrics[field] = {
            "weighted_cohen_kappa": cohen_kappa_score(human, judge, weights="quadratic"),
            "spearman_correlation": spearmanr(human, judge).statistic,
        }

    result = {
        "human_reviewed_rows": len(human_rows),
        "joined_rows": len(joined),
        "metrics": metrics,
        "note": "Agreement statistics are descriptive; no statistical significance is claimed.",
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
