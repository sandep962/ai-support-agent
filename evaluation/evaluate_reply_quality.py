"""Evaluate NO_RAG and RAG replies independently with the local LLM judge."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.reply_judge import ReplyJudge


def mean(scores: list[int]) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROJECT_ROOT / "results" / "reply_predictions.csv"))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "results" / "reply_judge_scores.csv"))
    parser.add_argument("--results", default=str(PROJECT_ROOT / "results" / "reply_judge_results.json"))
    args = parser.parse_args()

    with Path(args.input).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 50:
        raise ValueError(f"Expected 50 reply examples, found {len(rows)}")

    judge = ReplyJudge()
    scores: list[dict[str, int | str]] = []
    for number, row in enumerate(rows, 1):
        retrieved_cases = json.loads(row["retrieved_cases"])
        for system, reply, evidence in (
            ("NO_RAG", row["no_rag_reply"], []),
            ("RAG", row["rag_reply"], retrieved_cases),
        ):
            score = judge.score(row["customer_text"], reply, evidence)
            scores.append({"example_id": row["example_id"], "system": system, **score.as_dict()})
            print(f"Judged {number}/50 {system}", flush=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["example_id", "system", "relevance", "groundedness", "tone", "overall", "reason"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(scores)

    by_system = {
        system: [row for row in scores if row["system"] == system]
        for system in ("NO_RAG", "RAG")
    }
    summary: dict[str, object] = {"model": judge.model, "examples": len(rows), "judgments": len(scores)}
    for system, system_scores in by_system.items():
        summary[system] = {
            "mean_relevance": mean([int(row["relevance"]) for row in system_scores]),
            "mean_groundedness": mean([int(row["groundedness"]) for row in system_scores]),
            "mean_tone": mean([int(row["tone"]) for row in system_scores]),
            "mean_overall": mean([int(row["overall"]) for row in system_scores]),
            "median_overall": statistics.median([int(row["overall"]) for row in system_scores]),
        }
    no_rag = {row["example_id"]: int(row["overall"]) for row in by_system["NO_RAG"]}
    rag = {row["example_id"]: int(row["overall"]) for row in by_system["RAG"]}
    differences = [rag[example_id] - no_rag[example_id] for example_id in no_rag]
    summary["paired_comparison"] = {
        "rag_overall_greater": sum(difference > 0 for difference in differences),
        "no_rag_overall_greater": sum(difference < 0 for difference in differences),
        "tied": sum(difference == 0 for difference in differences),
        "average_score_difference_rag_minus_no_rag": mean(differences),
    }
    summary["note"] = "Scores are LLM-judge outputs; no statistical significance is claimed."
    Path(args.results).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()