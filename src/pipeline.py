"""End-to-end one-message Hiver support-agent pipeline."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ai_intent_classifier import AIIntentClassifier
from src.escalation import EscalationPredictor
from src.reply_generator import ReplyGenerator
from src.retrieval import HistoricalCaseRetriever


class SupportAgentPipeline:
    """Classify, retrieve evidence, draft a grounded reply, and assess escalation."""

    def __init__(
        self,
        golden_path: Path | None = None,
        corpus_path: Path | None = None,
    ) -> None:
        self.classifier = AIIntentClassifier()
        self.retriever = HistoricalCaseRetriever(
            corpus_path or PROJECT_ROOT / "results" / "apple_support" / "apple_support_pairs.csv",
            golden_path or PROJECT_ROOT / "evaluation" / "golden_set.csv",
        )
        self.reply_generator = ReplyGenerator()
        self.escalation_predictor = EscalationPredictor()

    def predict(self, customer_text: str) -> dict[str, Any]:
        if not customer_text or not customer_text.strip():
            raise ValueError("customer_text must be a non-empty string")

        intent = self.classifier.classify(customer_text)
        cases, _ = self.retriever.retrieve(customer_text, intent.intent, top_k=3)
        reply = self.reply_generator.generate(customer_text, intent.intent, cases)
        escalation = self.escalation_predictor.predict(customer_text)
        result = {
            "intent": intent.intent,
            "confidence": intent.confidence,
            "draft_reply": reply.draft_reply,
            "escalate": escalation.escalate,
            "escalation_reason": escalation.escalation_reason,
            "evidence": [case.as_dict() for case in cases],
        }
        self._validate(result, cases)
        return result

    @staticmethod
    def _validate(result: dict[str, Any], cases: list[Any]) -> None:
        expected_keys = {"intent", "confidence", "draft_reply", "escalate", "escalation_reason", "evidence"}
        if set(result) != expected_keys:
            raise ValueError(f"Unexpected pipeline keys: {sorted(result)}")
        if not isinstance(result["intent"], str) or not 0 <= float(result["confidence"]) <= 1:
            raise ValueError("Invalid intent prediction fields")
        if not isinstance(result["draft_reply"], str) or not result["draft_reply"].strip():
            raise ValueError("draft_reply must be non-empty")
        if not isinstance(result["escalate"], bool) or not result["escalation_reason"].strip():
            raise ValueError("Invalid escalation fields")
        evidence = result["evidence"]
        if not isinstance(evidence, list) or len(evidence) != len(cases):
            raise ValueError("Invalid evidence list")
        evidence_keys = {"customer_tweet_id", "historical_customer_text", "historical_support_text", "similarity_score"}
        for item in evidence:
            if set(item) != evidence_keys or not isinstance(item["customer_tweet_id"], str):
                raise ValueError("Invalid evidence item")


def main() -> None:
    messages = (
        "My iPhone keeps freezing after the latest iOS update.",
        "I cannot access my Apple ID because I no longer receive the verification code.",
        "I was charged for an order I canceled and need help with the refund.",
    )
    pipeline = SupportAgentPipeline()
    for index, message in enumerate(messages, 1):
        print(f"SMOKE_TEST_{index}")
        print(json.dumps(pipeline.predict(message), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()