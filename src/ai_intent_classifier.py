"""LLM-only intent classification for the frozen AppleSupport taxonomy.

The classifier accepts customer_text only. It has no access to historical
support replies, silver data, candidate provenance, notes, or golden labels.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LABELS = ("1", "2", "3", "4", "5", "6", "7", "8", "OTHER_OR_AMBIGUOUS")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

INSTRUCTIONS = """You classify a single Apple customer-support tweet using only the tweet text.

Frozen taxonomy:
1 = Device hardware / charging / physical functionality
2 = iOS and software behavior / updates
3 = Apple ID and account access
4 = iCloud, backup, restore, and data sync
5 = Apps / App Store / media downloads
6 = Billing, payments, subscriptions, refunds
7 = Connectivity: Wi-Fi / Bluetooth / cellular / calls
8 = Orders, repair, replacement, store, delivery
OTHER_OR_AMBIGUOUS = unclear/insufficient information

For multi-issue tweets, choose the primary reason the customer needs support.
Do not infer an issue that is not present. If the message is too vague or has
insufficient evidence, use OTHER_OR_AMBIGUOUS. Do not use any context beyond
the supplied customer text. Confidence must be between 0 and 1. Keep the reason
brief and grounded in the text.
Return exactly one JSON object with the keys intent, confidence, and reason.
Do not include markdown, commentary, or any additional keys.
"""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {"type": "string", "enum": list(LABELS)},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
    },
    "required": ["intent", "confidence", "reason"],
}


@dataclass(frozen=True)
class Prediction:
    intent: str
    confidence: float
    reason: str


class AIIntentClassifier:
    def __init__(self, model: str = MODEL, max_retries: int = 3) -> None:
        self.model = model
        self.max_retries = max_retries

    def classify(self, customer_text: str) -> Prediction:
        request_body = {
            "model": self.model,
            "system": INSTRUCTIONS,
            "prompt": f"Customer tweet:\n{customer_text}",
            "format": SCHEMA,
            "stream": False,
            "options": {"temperature": 0},
        }
        for attempt in range(self.max_retries):
            try:
                request = Request(
                    f"{OLLAMA_HOST}/api/generate",
                    data=json.dumps(request_body).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=120) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                prediction_payload = json.loads(payload["response"])
                prediction = Prediction(
                    intent=str(prediction_payload["intent"]),
                    confidence=float(prediction_payload["confidence"]),
                    reason=str(prediction_payload["reason"]),
                )
                if prediction.intent not in LABELS or not 0 <= prediction.confidence <= 1:
                    raise ValueError(f"Invalid structured prediction: {prediction_payload}")
                return prediction
            except (HTTPError, URLError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")
