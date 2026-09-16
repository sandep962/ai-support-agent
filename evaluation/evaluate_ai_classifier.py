"""Run the held-out golden set through the LLM classifier and calculate metrics."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from src.ai_intent_classifier import AIIntentClassifier, LABELS, MODEL


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", default=str(PROJECT_ROOT / "evaluation" / "golden_set.csv"))
    parser.add_argument("--predictions", default=str(PROJECT_ROOT / "results" / "ai_classifier_predictions.csv"))
    parser.add_argument("--results", default=str(PROJECT_ROOT / "results" / "ai_classifier_results.json"))
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    with Path(args.golden).open(encoding="utf-8-sig", newline="") as fh:
        golden = [row for row in csv.DictReader(fh) if row.get("customer_text", "").strip() and row.get("human_label", "").strip()]
    if not golden:
        raise ValueError("Golden set has no labeled customer_text rows")

    classifier = AIIntentClassifier(model=args.model)
    predictions: list[dict[str, str]] = [None] * len(golden)  # type: ignore[list-item]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(classifier.classify, row["customer_text"]): index for index, row in enumerate(golden)}
        for completed, future in enumerate(as_completed(futures), 1):
            index = futures[future]
            prediction = future.result()
            row = golden[index]
            predictions[index] = {
                "example_id": row.get("example_id", ""), "customer_text": row["customer_text"],
                "gold_label": row["human_label"], "predicted_label": prediction.intent,
                "confidence": f"{prediction.confidence:.6f}", "reason": prediction.reason,
            }
            print(f"Completed {completed}/{len(golden)}", flush=True)

    Path(args.predictions).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.predictions).open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["example_id", "customer_text", "gold_label", "predicted_label", "confidence", "reason"])
        writer.writeheader(); writer.writerows(predictions)

    y_true = [row["gold_label"] for row in predictions]
    y_pred = [row["predicted_label"] for row in predictions]
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, labels=list(LABELS), average="macro", zero_division=0)
    result = {
        "model": args.model, "golden_rows": len(predictions),
        "accuracy": accuracy_score(y_true, y_pred), "macro_precision": p, "macro_recall": r, "macro_f1": f1,
        "confidence_at_least_0_8": sum(float(row["confidence"]) >= 0.8 for row in predictions),
        "confidence_at_least_0_9": sum(float(row["confidence"]) >= 0.9 for row in predictions),
        "labels": list(LABELS),
        "per_class": classification_report(y_true, y_pred, labels=list(LABELS), output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=list(LABELS)).tolist(),
        "comparison": {"majority": {"accuracy": 0.248, "macro_f1": 0.0441595}, "tfidf_logistic": {"accuracy": 0.624, "macro_f1": 0.5647142}},
    }
    Path(args.results).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("model", "golden_rows", "accuracy", "macro_precision", "macro_recall", "macro_f1", "confidence_at_least_0_8", "confidence_at_least_0_9")}, indent=2))


if __name__ == "__main__":
    main()
