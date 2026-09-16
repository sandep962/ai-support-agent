"""Grounded draft-reply generation through the local Ollama API."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen

from src.retrieval import RetrievedCase

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

REPLY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "draft_reply": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["draft_reply", "evidence_ids"],
}

INSTRUCTIONS = """You are an Apple customer-support representative drafting a concise, helpful reply.
Use historical examples as evidence of how similar issues were handled.
Do not invent policies, refunds, guarantees, features, or troubleshooting steps unsupported by the evidence.
Do not copy historical replies verbatim. If the evidence is insufficient, say so rather than inventing an answer.
When no historical evidence is supplied, do not state an unsupported diagnosis, limitation, URL, or resolution; acknowledge the issue and ask for useful details instead.
Do not mention that you are an AI. Do not claim to have performed an action you cannot perform.
Return exactly one JSON object with draft_reply and evidence_ids, with no markdown or extra keys.
"""


@dataclass(frozen=True)
class ReplyPrediction:
    draft_reply: str
    evidence_ids: list[str]


class ReplyGenerator:
    def __init__(self, model: str = MODEL, host: str = OLLAMA_HOST) -> None:
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, customer_text: str, predicted_intent: str, cases: list[RetrievedCase] | None = None) -> ReplyPrediction:
        cases = cases or []
        evidence = "\n\n".join(
            f"Evidence {case.customer_tweet_id}:\nCustomer: {case.historical_customer_text}\nApple response: {case.historical_support_text}"
            for case in cases
        ) or "No historical evidence was supplied."
        prompt = (
            f"Customer tweet:\n{customer_text}\n\nPredicted intent: {predicted_intent}\n\n"
            f"Historical customer-support cases:\n{evidence}\n\n"
            "For evidence_ids, use only the historical customer tweet IDs supplied above."
        )
        request = Request(
            f"{self.host}/api/generate",
            data=json.dumps({
                "model": self.model,
                "system": INSTRUCTIONS,
                "prompt": prompt,
                "format": REPLY_SCHEMA,
                "stream": False,
                "options": {"temperature": 0},
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
        output = json.loads(payload["response"])
        reply = ReplyPrediction(str(output["draft_reply"]), [str(item) for item in output["evidence_ids"]])
        allowed_ids = {case.customer_tweet_id for case in cases}
        if not reply.draft_reply.strip():
            raise ValueError(f"Invalid reply output: {output}")
        if not cases:
            return ReplyPrediction(reply.draft_reply, [])
        return ReplyPrediction(reply.draft_reply, [item for item in reply.evidence_ids if item in allowed_ids])