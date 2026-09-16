"""Local Ollama escalation prediction using customer text only."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

ESCALATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "escalate": {"type": "boolean"},
        "escalation_reason": {"type": "string"},
    },
    "required": ["escalate", "escalation_reason"],
}

INSTRUCTIONS = """Decide whether this Apple customer-support message should be escalated to a human.
Use only the customer message. Do not use labels, intent names, historical replies, or hidden context.
Set escalate true when the issue reasonably requires human intervention, account-specific action, sensitive or security handling, transaction investigation, fraud or unauthorized activity handling, serious data-loss or recovery handling, physical repair or service intervention, legal or high-risk handling, or the customer explicitly requires human support after normal assistance.
Set escalate false for routine informational questions and routine troubleshooting that an automated support response can reasonably handle.
When uncertain, use the safest reasonable interpretation. Keep escalation_reason short and grounded in the message.
Return exactly one JSON object with only escalate and escalation_reason.
"""


@dataclass(frozen=True)
class EscalationPrediction:
    escalate: bool
    escalation_reason: str


class EscalationPredictor:
    def __init__(self, model: str = MODEL, host: str = OLLAMA_HOST, max_retries: int = 3) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.max_retries = max_retries

    def predict(self, customer_text: str) -> EscalationPrediction:
        request_body = {
            "model": self.model,
            "system": INSTRUCTIONS,
            "prompt": f"Customer message:\n{customer_text}",
            "format": ESCALATION_SCHEMA,
            "stream": False,
            "options": {"temperature": 0},
        }
        for attempt in range(self.max_retries):
            try:
                request = Request(
                    f"{self.host}/api/generate",
                    data=json.dumps(request_body).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=180) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                output = json.loads(payload["response"])
                if not isinstance(output["escalate"], bool):
                    raise ValueError(f"Escalate must be boolean: {output}")
                prediction = EscalationPrediction(output["escalate"], str(output["escalation_reason"]))
                if not prediction.escalation_reason.strip():
                    raise ValueError(f"Empty escalation reason: {output}")
                return prediction
            except (HTTPError, URLError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")