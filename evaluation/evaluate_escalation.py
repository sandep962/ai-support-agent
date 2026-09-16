"""Evaluate binary escalation predictions against manually reviewed labels."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.escalation import EscalationPredictor


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default=str(PROJECT_ROOT / "evaluation" / "escalation_labeling.csv"))
    parser.add_argument("--predictions", default=str(PROJECT_ROOT / "results" / "escalation_predictions.csv"))
    parser.add_argument("--results", default=str(PROJECT_ROOT / "results" / "escalation_results.json"))
    args = parser.parse_args()

    labels = read_csv(Path(args.labels))
    if len(labels) != 250:
        raise ValueError(f"Expected exactly 250 escalation labels, found {len(labels)}")
    if any(not row.get("escalate_gold", "").strip() for row in labels):
        raise ValueError("All escalate_gold fields must be completed before evaluation")

    predictor = EscalationPredictor()
    predictions = []
    for number, row in enumerate(labels, 1):
        prediction = predictor.predict(row["customer_text"])
        predictions.append({
            "example_id": row["example_id"],
            "customer_text": row["customer_text"],
            "predicted_escalation": int(prediction.escalate),
            "escalation_reason": prediction.escalation_reason,
        })
        print(f"Predicted {number}/{len(labels)}", flush=True)
    predictions_path = Path(args.predictions)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    with predictions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)

    label_by_id = {row["example_id"]: row for row in labels}
    joined: list[tuple[int, int]] = []
    for row in predictions:
        example_id = row["example_id"]
        if example_id not in label_by_id:
            raise ValueError(f"Prediction has no matching label: {example_id}")
        joined.append((int(label_by_id[example_id]["escalate_gold"]), int(row["predicted_escalation"])))

    y_true = [pair[0] for pair in joined]
    y_pred = [pair[1] for pair in joined]
    if any(value not in (0, 1) for value in y_true + y_pred):
        raise ValueError("Escalation labels and predictions must be 0 or 1")
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    true_negative, false_positive, false_negative, true_positive = matrix.ravel()
    result = {
        "model": predictor.model,
        "rows": len(joined),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "false_negative_rate": false_negative / (false_negative + true_positive) if false_negative + true_positive else 0.0,
        "confusion_matrix_labels": [0, 1],
        "confusion_matrix": matrix.tolist(),
        "counts": {
            "true_negative": int(true_negative),
            "false_positive": int(false_positive),
            "false_negative": int(false_negative),
            "true_positive": int(true_positive),
        },
        "note": "For escalation, recall and false-negative rate are highlighted because missed escalations are higher risk than unnecessary escalations.",
    }
    analysis_path = PROJECT_ROOT / "analysis" / "escalation_failure_analysis.md"
    false_positives = [
        (label_by_id[row["example_id"]], row)
        for row in predictions
        if int(label_by_id[row["example_id"]]["escalate_gold"]) == 0 and int(row["predicted_escalation"]) == 1
    ]
    false_negatives = [
        (label_by_id[row["example_id"]], row)
        for row in predictions
        if int(label_by_id[row["example_id"]]["escalate_gold"]) == 1 and int(row["predicted_escalation"]) == 0
    ]
    analysis_lines = [
        "# Escalation Failure Analysis",
        "",
        f"Evaluated rows: {len(joined)}",
        f"False positives: {false_positive}",
        f"False negatives: {false_negative}",
        "",
        "## Representative False Positives",
        "",
    ]
    for gold_row, prediction in false_positives[:5]:
        analysis_lines.extend([
            f"### {prediction['example_id']}",
            f"- Customer text: {prediction['customer_text']}",
            f"- Gold escalation: `{gold_row['escalate_gold']}`",
            f"- Predicted escalation: `{prediction['predicted_escalation']}`",
            f"- Gold reason: {gold_row['escalation_reason']}",
            f"- Model reason: {prediction['escalation_reason']}",
            "",
        ])
    analysis_lines.extend(["## Representative False Negatives", ""])
    for gold_row, prediction in false_negatives[:5]:
        analysis_lines.extend([
            f"### {prediction['example_id']}",
            f"- Customer text: {prediction['customer_text']}",
            f"- Gold escalation: `{gold_row['escalate_gold']}`",
            f"- Predicted escalation: `{prediction['predicted_escalation']}`",
            f"- Gold reason: {gold_row['escalation_reason']}",
            f"- Model reason: {prediction['escalation_reason']}",
            "",
        ])
    analysis_path.parent.mkdir(parents=True, exist_ok=True)
    analysis_path.write_text("\n".join(analysis_lines), encoding="utf-8")
    output = Path(args.results)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
