# Final Failure Analysis

This summary uses the completed intent, reply, judge-agreement, and escalation artifacts. It describes observed failures and testable mitigation hypotheses; it does not claim that any mitigation has been implemented or validated.

## 1. Intent errors collapse explicit multi-issue messages into ambiguity

**Metric/evidence:** The Ollama intent classifier made `119/250` errors. Its largest error sink was `OTHER_OR_AMBIGUOUS` with `42` incorrect predictions. The top confusion pairs included `1 -> OTHER_OR_AMBIGUOUS` (`13`), `7 -> OTHER_OR_AMBIGUOUS` (`11`), and `2 -> OTHER_OR_AMBIGUOUS` (`8`).

**Examples:**

- `APPLE-GOLD-002`: “WiFi & calling broken, 50% increase in battery drain, iOS freezes.” Gold intent `7`; predicted `OTHER_OR_AMBIGUOUS` at confidence `0.8`, with reason “unclear/insufficient information.”
- `APPLE-GOLD-004`: “Any fix for the battery drain?” Gold intent `1`; predicted `OTHER_OR_AMBIGUOUS` at confidence `0.8`, with the same reason.

**Observed result:** Messages with several issue cues, or even a short explicit battery complaint, were sometimes rejected as ambiguous instead of assigned to the reviewed primary intent.

**Hypothesis:** The fixed single-label task forces a primary-intent decision on noisy, abbreviated, multi-issue tweets. The model appears conservative in some cases and treats multiple cues or sparse context as insufficient evidence.

**Concrete mitigation:** Add a held-out ambiguity/multi-issue error slice and require structured primary-intent reasoning during development. Compare calibrated confidence and targeted prompt variants against that slice without changing the frozen taxonomy.

## 2. High confidence does not reliably indicate correct intent

**Metric/evidence:** There were `103` wrong predictions with confidence `>= 0.8`, including `22` with confidence `>= 0.9`.

**Examples:**

- `APPLE-GOLD-068`: A two-factor authentication problem when the phone is dead. Gold `3`; predicted `4` at confidence `0.9`.
- `APPLE-GOLD-169`: A case blocks the microphone during calls and the customer asks about a refund. Gold `7`; predicted `4` at confidence `0.9`.

**Observed result:** The model was highly confident while selecting iCloud/data-sync intent for account-security and call/hardware-context messages.

**Hypothesis:** Confidence is a model-generated value rather than a validated probability. Salient words such as “codes,” “phone,” “case,” and “refund” can dominate the decision even when the reviewed primary intent differs.

**Concrete mitigation:** Treat confidence as an uncalibrated ranking signal until calibrated on a separate validation set. Add confidence-conditioned error reporting and abstention review; do not equate `0.9` with a 90% correctness guarantee.

## 3. Escalation misses the cases where human intervention matters

**Metric/evidence:** On `250` labeled messages, escalation accuracy was `0.812`, but recall was only `0.2909`, with `39` false negatives out of `55` gold escalations. The false-negative rate was `0.7091` (`70.91%`).

**Examples:**

- `APPLE-GOLD-063`: “Your verification code SMSs aren't being sent.” Gold escalation `1`; predicted `0` as routine troubleshooting.
- `APPLE-GOLD-064`: The customer no longer has access to the Apple ID email account. Gold `1`; predicted `0` as a routine informational question.

**Observed result:** The system produced only `16` true positives and `8` false positives, so the high accuracy is dominated by the `195` non-escalation examples.

**Hypothesis:** The predictor recognizes ordinary troubleshooting language but underweights account recovery, security, and access constraints when the message does not explicitly say “human.”

**Concrete mitigation:** Optimize escalation development for recall and false-negative review, especially for account recovery, verification, encrypted backups, physical defects, and unresolved prior support. Add a conservative rule or review gate for these evidence-backed high-risk patterns, then re-evaluate on a fresh held-out set.

## 4. Historical grounding can introduce irrelevant or unsupported reply content

**Metric/evidence:** In the 50-example reply experiment, the LLM judge gave RAG mean groundedness `4.38` versus `1.86` for NO_RAG, but human-vs-judge groundedness agreement was negative: weighted Cohen’s kappa `-0.1452` and Spearman correlation `-0.1364`. The human review also found concrete RAG errors.

**Examples:**

- `APPLE-GOLD-232`: The customer complained about an Apple Store appointment wait. The RAG reply introduced “iCloud Photo Library.” Human overall score was `2`, with a note that this was unrelated; the judge scored overall `4` and groundedness `5`.
- `APPLE-GOLD-184`: The RAG reply directed the customer to an “iTunes Store team” and a link. Human groundedness was `3` and overall `3`, noting that the routing claim was not clearly supported; the judge gave groundedness `5` and overall `4`.

**Observed result:** Retrieval can supply historically plausible support language that is not actually relevant to the current customer message.

**Hypothesis:** TF-IDF similarity and same-intent preference are lexical/retrieval heuristics, not factual entailment checks. The generator may copy the style or routing pattern of a retrieved case even when the evidence is only loosely related.

**Concrete mitigation:** Add evidence entailment checks before generation, require every factual action or routing claim to cite a specific retrieved response, and abstain from unsupported details. Measure groundedness with independent human review rather than relying on the LLM judge alone.

## 5. LLM-judge scores are not a reliable substitute for human quality review

**Metric/evidence:** Across `40` matched human/judge rows, agreement was low for relevance (`kappa 0.2569`), overall (`0.1228`), and groundedness (`-0.1452`). Tone kappa was `0.0`; tone Spearman correlation was undefined because one score series was constant.

**Examples:**

- `APPLE-GOLD-163` RAG: The reply incorrectly said the iPhone was “still going strong” and misunderstood the customer’s message. Human overall was `2`; the judge gave overall `4` and groundedness `5`.
- `APPLE-GOLD-025` RAG: Human overall was `4`; the judge gave overall `5`. The difference is smaller, but demonstrates that fluent, plausible drafts can receive systematically different ratings from humans.

**Observed result:** The judge comparison favored RAG: RAG overall mean `4.16` versus NO_RAG `3.78`, with RAG higher in `18`, NO_RAG higher in `0`, and `32` ties. The low human agreement limits how strongly that result should be interpreted.

**Hypothesis:** The judge rewards professional support style and historical-looking evidence, while humans notice message-specific misreadings and unsupported details. The judge also saw a structured evidence presentation that may have influenced its groundedness assessment.

**Concrete mitigation:** Keep human review as the acceptance gate, use multiple blinded judges or adjudication for important releases, and report judge-human agreement alongside every automated quality comparison.

## Summary

The strongest operational failure is escalation recall: `39` gold escalations were missed. The strongest intent failures are ambiguity collapse and high-confidence misclassification. RAG improved automated judged scores in this sample, but human disagreement shows that retrieval and judge fluency are not proof of correct or safe support behavior.