"""Blind LLM-as-judge scoring for generated customer-support replies."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "relevance": {"type": "integer", "minimum": 1, "maximum": 5},
        "groundedness": {"type": "integer", "minimum": 1, "maximum": 5},
        "tone": {"type": "integer", "minimum": 1, "maximum": 5},
        "overall": {"type": "integer", "minimum": 1, "maximum": 5},
        "reason": {"type": "string"},
    },
    "required": ["relevance", "groundedness", "tone", "overall", "reason"],
}

JUDGE_INSTRUCTIONS = """You are an impartial evaluator of one Apple customer-support draft reply.
Judge this one reply independently. You will not see any alternative reply.
Do not use gold labels, predicted intents, or any hidden expected outcome.
Do not reward fluency alone.

Score each dimension from 1 to 5:
1. Relevance: directly addresses the customer's issue.
2. Groundedness: factual claims and suggested actions are supported by the supplied customer message and, when present, historical evidence. For no-evidence cases, penalize unsupported factual claims.
3. Tone: professional, empathetic, concise, and appropriate for customer support.
4. Overall: overall usefulness and quality as a customer-support draft.

For historical evidence, judge whether it actually supports the reply. If evidence is absent, do not assume facts beyond the customer message.
Return exactly one JSON object with integer scores from 1 to 5 and a short evidence-based reason. Do not include markdown or extra keys.
"""


@dataclass(frozen=True)
class JudgeScore:
    relevance: int
    groundedness: int
    tone: int
    overall: int
    reason: str

    def as_dict(self) -> dict[str, int | str]:
        return {
            "relevance": self.relevance,
            "groundedness": self.groundedness,
            "tone": self.tone,
            "overall": self.overall,
            "reason": self.reason,
        }


class ReplyJudge:
    def __init__(self, model: str = MODEL, host: str = OLLAMA_HOST) -> None:
        self.model = model
        self.host = host.rstrip("/")

    def score(self, customer_text: str, reply: str, evidence: list[dict[str, str]] | None = None) -> JudgeScore:
        evidence = evidence or []
        evidence_text = "\n\n".join(
            f"Historical case {case['customer_tweet_id']}:\n"
            f"Customer: {case['historical_customer_text']}\n"
            f"Apple response: {case['historical_support_text']}"
            for case in evidence
        ) or "No historical evidence was provided."
        prompt = (
            f"Customer message:\n{customer_text}\n\n"
            f"Draft reply to evaluate:\n{reply}\n\n"
            f"Historical evidence available to this reply:\n{evidence_text}"
        )
        request = Request(
            f"{self.host}/api/generate",
            data=json.dumps({
                "model": self.model,
                "system": JUDGE_INSTRUCTIONS,
                "prompt": prompt,
                "format": JUDGE_SCHEMA,
                "stream": False,
                "options": {"temperature": 0},
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
        output = json.loads(payload["response"])
        score = JudgeScore(
            relevance=int(output["relevance"]),
            groundedness=int(output["groundedness"]),
            tone=int(output["tone"]),
            overall=int(output["overall"]),
            reason=str(output["reason"]),
        )
        if any(value < 1 or value > 5 for value in (score.relevance, score.groundedness, score.tone, score.overall)):
            raise ValueError(f"Invalid judge score: {output}")
        if not score.reason.strip():
            raise ValueError(f"Judge reason is empty: {output}")
        return score