"""Run the no-RAG versus historical-grounded reply experiment."""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.reply_generator import ReplyGenerator
from src.retrieval import HistoricalCaseRetriever


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row.get("customer_text", "").strip()]


def select_subset(golden: list[dict[str, str]], predictions: dict[str, dict[str, str]], size: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    groups: dict[str, list[dict[str, str]]] = {}
    for row in golden:
        gold_intent = row.get("gold_intent") or row.get("human_label") or "OTHER_OR_AMBIGUOUS"
        groups.setdefault(gold_intent, []).append(row)
    for rows in groups.values():
        rng.shuffle(rows)
    selected: list[dict[str, str]] = []
    while len(selected) < size and any(groups.values()):
        for label in sorted(groups):
            if groups[label] and len(selected) < size:
                row = groups[label].pop()
                if row["example_id"] in predictions:
                    selected.append(row)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--golden", default=str(PROJECT_ROOT / "evaluation" / "golden_set.csv"))
    parser.add_argument("--predictions", default=str(PROJECT_ROOT / "results" / "ai_classifier_predictions.csv"))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "results" / "reply_predictions.csv"))
    parser.add_argument("--results", default=str(PROJECT_ROOT / "results" / "reply_results.json"))
    parser.add_argument("--corpus", default=str(PROJECT_ROOT / "results" / "apple_support" / "apple_support_pairs.csv"))
    args = parser.parse_args()

    golden = load_rows(Path(args.golden))
    if len(golden) != 250:
        raise ValueError(f"Expected exactly 250 golden rows, found {len(golden)}")
    classifier_predictions = {row["example_id"]: row for row in load_rows(Path(args.predictions))}
    selected = select_subset(golden, classifier_predictions, args.limit, args.seed)
    if len(selected) != args.limit:
        raise ValueError(f"Could select only {len(selected)} rows")

    retriever = HistoricalCaseRetriever(Path(args.corpus), Path(args.golden))
    generator = ReplyGenerator()
    output_rows: list[dict[str, str]] = []
    similarities: list[float] = []
    same_intent_available = 0
    no_rag_failures = 0
    rag_failures = 0
    for number, row in enumerate(selected, 1):
        predicted_intent = classifier_predictions[row["example_id"]]["predicted_label"]
        cases, same_intent = retriever.retrieve(row["customer_text"], predicted_intent)
        same_intent_available += int(same_intent)
        similarities.extend(case.similarity_score for case in cases)
        try:
            no_rag = generator.generate(row["customer_text"], predicted_intent)
        except Exception as error:
            no_rag_failures += 1
            no_rag = type("FailedReply", (), {"draft_reply": f"ERROR: {error}", "evidence_ids": []})()
        try:
            rag = generator.generate(row["customer_text"], predicted_intent, cases)
        except Exception as error:
            rag_failures += 1
            rag = type("FailedReply", (), {"draft_reply": f"ERROR: {error}", "evidence_ids": []})()
        output_rows.append({
            "example_id": row["example_id"],
            "customer_text": row["customer_text"],
            "gold_intent": row.get("gold_intent") or row.get("human_label", ""),
            "predicted_intent": predicted_intent,
            "no_rag_reply": no_rag.draft_reply,
            "rag_reply": rag.draft_reply,
            "evidence_ids": json.dumps(rag.evidence_ids),
            "retrieved_cases": json.dumps([case.as_dict() for case in cases], ensure_ascii=False),
        })
        print(f"Completed {number}/{len(selected)}", flush=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader(); writer.writerows(output_rows)
    result = {
        "model": generator.model,
        "examples": len(output_rows),
        "successful_generations": (len(output_rows) * 2) - no_rag_failures - rag_failures,
        "successful_examples": len(output_rows) - sum(
            row["no_rag_reply"].startswith("ERROR:") or row["rag_reply"].startswith("ERROR:")
            for row in output_rows
        ),
        "failed_generations": no_rag_failures + rag_failures,
        "no_rag_failed": no_rag_failures,
        "rag_failed": rag_failures,
        "retrieval_statistics": {
            "eligible_historical_pairs": len(retriever.cases),
            "retrieved_cases": sum(len(json.loads(row["retrieved_cases"])) for row in output_rows),
            "average_retrieval_similarity": sum(similarities) / len(similarities) if similarities else 0.0,
            "same_intent_historical_cases_available": same_intent_available,
        },
        "selection_seed": args.seed,
        "comparison_note": "This experiment saves outputs only; no claim about reply quality improvement is made.",
    }
    Path(args.results).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()