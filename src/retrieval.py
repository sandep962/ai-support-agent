"""CPU-reproducible retrieval of historical Apple customer-support cases."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LABELS = ("1", "2", "3", "4", "5", "6", "7", "8", "OTHER_OR_AMBIGUOUS")


@dataclass(frozen=True)
class RetrievedCase:
    customer_tweet_id: str
    historical_customer_text: str
    historical_support_text: str
    similarity_score: float

    def as_dict(self) -> dict[str, str | float]:
        return {
            "customer_tweet_id": self.customer_tweet_id,
            "historical_customer_text": self.historical_customer_text,
            "historical_support_text": self.historical_support_text,
            "similarity_score": round(self.similarity_score, 6),
        }


@dataclass(frozen=True)
class _HistoricalCase:
    conversation_id: str
    customer_tweet_id: str
    customer_text: str
    support_text: str
    inferred_intent: str


def _contains(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def infer_historical_intent(customer_text: str) -> str:
    """Infer a retrieval preference from transparent text cues, never labels."""
    text = customer_text or ""
    rules = (
        ("8", (r"\border\b", r"pre[- ]?order", r"repair", r"replacement", r"replace", r"delivery", r"shipping", r"store appointment")),
        ("6", (r"refund", r"billing", r"charged", r"payment", r"subscription", r"invoice", r"purchase")),
        ("3", (r"apple id", r"password", r"sign[ -]?in", r"login", r"two[- ]factor", r"verification", r"account")),
        ("4", (r"icloud", r"backup", r"restore", r"sync", r"missing photos", r"data")),
        ("7", (r"wi[- ]?fi", r"bluetooth", r"cellular", r"calls?", r"signal", r"network", r"no sim")),
        ("5", (r"app store", r"download", r"install", r"apple music", r"itunes", r"app\b", r"apps\b")),
        ("2", (r"ios", r"software", r"update", r"upgrade", r"freeze", r"crash", r"bug", r"glitch")),
        ("1", (r"battery", r"charg", r"screen", r"camera", r"speaker", r"microphone", r"hardware", r"headphone")),
    )
    matches = [label for label, patterns in rules if _contains(text, patterns)]
    return matches[0] if len(matches) == 1 else "OTHER_OR_AMBIGUOUS"


class HistoricalCaseRetriever:
    def __init__(self, corpus_path: Path, golden_path: Path) -> None:
        golden_ids: set[str] = set()
        with golden_path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("customer_tweet_id", "").strip():
                    golden_ids.add(row["customer_tweet_id"].strip())

        raw_rows = list(csv.DictReader(corpus_path.open(encoding="utf-8-sig", newline="")))
        golden_conversations = {
            row.get("conversation_id", "") for row in raw_rows
            if row.get("customer_tweet_id", "") in golden_ids
        }
        self.cases = [
            _HistoricalCase(
                conversation_id=row["conversation_id"],
                customer_tweet_id=row["customer_tweet_id"],
                customer_text=row["customer_text"],
                support_text=row["support_text"],
                inferred_intent=infer_historical_intent(row["customer_text"]),
            )
            for row in raw_rows
            if row.get("customer_tweet_id") not in golden_ids
            and row.get("conversation_id") not in golden_conversations
            and row.get("customer_text", "").strip()
            and row.get("support_text", "").strip()
        ]
        if not self.cases:
            raise ValueError("Historical corpus has no eligible customer-support pairs")
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
        self.matrix = self.vectorizer.fit_transform(case.customer_text for case in self.cases)
        self.intent_counts = {label: sum(case.inferred_intent == label for case in self.cases) for label in LABELS}

    def retrieve(self, customer_text: str, predicted_intent: str, top_k: int = 3) -> tuple[list[RetrievedCase], bool]:
        query = self.vectorizer.transform([customer_text])
        scores = cosine_similarity(query, self.matrix).ravel()
        ranked = sorted(range(len(self.cases)), key=lambda index: scores[index], reverse=True)
        same_intent_available = self.intent_counts.get(predicted_intent, 0) > 0
        same_intent = [index for index in ranked if self.cases[index].inferred_intent == predicted_intent]
        other = [index for index in ranked if self.cases[index].inferred_intent != predicted_intent]
        selected = (same_intent + other)[:top_k] if same_intent else ranked[:top_k]
        return [
            RetrievedCase(
                customer_tweet_id=self.cases[index].customer_tweet_id,
                historical_customer_text=self.cases[index].customer_text,
                historical_support_text=self.cases[index].support_text,
                similarity_score=float(scores[index]),
            )
            for index in selected
        ], same_intent_available