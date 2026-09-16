# 1. Problem framing

Good support-agent behavior means correctly identifying the customer's primary need, drafting a concise reply grounded in how Apple historically handled similar cases, and routing high-risk or account-specific issues to a human instead of confidently mishandling them. Quality is multidimensional: intent accuracy, reply relevance and groundedness, and escalation recall matter more than fluent text or aggregate accuracy alone.

This project evaluates three tasks:

1. **Intent classification:** assign one of the frozen eight intents plus `OTHER_OR_AMBIGUOUS`.
2. **Historically grounded reply drafting:** retrieve similar Apple customer-to-support cases and use the historical Apple response as evidence for a draft reply.
3. **Auto-handle versus human escalation:** decide whether an automated response is reasonable or whether a human should intervene.

The scope is one brand, Apple Support. Historical customer-to-support pairs were reconstructed from TWCS inbound customer messages and outbound `AppleSupport` responses. The intent evaluation uses a held-out 250-row golden set. The reply experiment uses a deterministic 50-example subset, and escalation uses the 250 manually labeled escalation examples.

The project deliberately did not build a frontend, API server, deployment system, authentication, reply-generation product workflow, or production policy layer. Those were outside this assignment phase; the work focused on reproducible model behavior, historical grounding, failure analysis, and evaluation.

# 2. Results vs baselines

## Intent classification

| System | Accuracy | Macro F1 |
|---|---:|---:|
| Majority baseline | 0.248 | 0.0441595 |
| TF-IDF + Logistic Regression | 0.624 | 0.5647142 |
| Llama 3.2 | 0.524 | 0.5159378 |

The Llama classifier did **not** beat the simple TF-IDF + Logistic Regression baseline. The baseline reached both higher accuracy and higher macro F1 on the 250-row golden evaluation.

## Reply generation

The reply experiment evaluated 50 golden examples with the same Llama 3.2 model in NO_RAG and RAG conditions. These are LLM-judge results, not definitive human-quality measurements.

| Metric | NO_RAG | RAG |
|---|---:|---:|
| Mean overall | 3.78 | 4.16 |
| Mean groundedness | 1.86 | 4.38 |
| Mean relevance | 3.60 | 4.16 |
| Mean tone | 4.98 | 5.00 |
| Median overall | 4.0 | 4.0 |

RAG was higher overall in `18` examples, NO_RAG was higher in `0`, and `32` were tied. The average overall difference was `+0.38` for RAG minus NO_RAG. These results show what the LLM judge preferred in this sample; they do not establish that RAG improves real customer-facing quality.

## Human versus LLM-judge agreement

Agreement was calculated on 40 human-reviewed replies joined by `example_id + system`.

| Dimension | Weighted Cohen's kappa | Spearman correlation |
|---|---:|---:|
| Relevance | 0.2569 | 0.2443 |
| Groundedness | -0.1452 | -0.1364 |
| Tone | 0.0000 | Not defined because one score series was constant |
| Overall | 0.1228 | 0.1614 |

The low agreement limits confidence in the LLM judge as a substitute for human review. In particular, negative groundedness agreement means that the automated RAG comparison should be treated as provisional.

## Escalation

| Metric | Result |
|---|---:|
| Accuracy | 0.812 |
| Precision | 0.6667 |
| Recall | 0.2909 |
| F1 | 0.4051 |
| False positives | 8 |
| False negatives | 39 |
| False-negative rate | 0.7091 |

The confusion matrix, with rows as gold `[0, 1]` and columns as predicted `[0, 1]`, is:

```text
[[187, 8],
 [39, 16]]
```

Accuracy is misleading here because the set contains `195` non-escalation examples and only `55` escalation examples. Predicting non-escalation often produces high accuracy while missing the cases that matter operationally. Recall and false-negative rate are more important: the system missed `39` gold escalation cases, producing a `70.91%` false-negative rate.

# 3. Top 5 failure modes

The complete evidence-backed analysis is preserved in [analysis/final_failure_analysis.md](../analysis/final_failure_analysis.md). The five observed failure modes are:

## 1. Intent errors collapse explicit multi-issue messages into ambiguity

The intent classifier made `119/250` errors. `OTHER_OR_AMBIGUOUS` accounted for `42` incorrect predictions; the largest confusion pairs were `1 -> OTHER_OR_AMBIGUOUS` (`13`), `7 -> OTHER_OR_AMBIGUOUS` (`11`), and `2 -> OTHER_OR_AMBIGUOUS` (`8`). `APPLE-GOLD-002` was a Wi-Fi/calling/battery/iOS message predicted as ambiguous at confidence `0.8`; `APPLE-GOLD-004` was an explicit battery-drain message predicted as ambiguous at confidence `0.8`.

The recorded hypothesis is that one primary label must be chosen for noisy multi-issue text, and the model sometimes treats multiple cues or sparse context as insufficient. The recorded mitigation is a held-out ambiguity/multi-issue slice with calibrated confidence and targeted prompt comparisons.

## 2. High confidence does not reliably indicate correct intent

There were `103` wrong predictions at confidence `>= 0.8`, including `22` at `>= 0.9`. `APPLE-GOLD-068` was an account two-factor problem predicted as intent `4` at `0.9`; `APPLE-GOLD-169` was a call/microphone issue with refund language predicted as intent `4` at `0.9`.

The recorded hypothesis is that generated confidence is not calibrated probability and salient words can dominate the decision. The recorded mitigation is calibration, confidence-conditioned error reporting, and abstention review.

## 3. Escalation misses cases requiring human intervention

The escalation system had `39` false negatives and a `0.7091` false-negative rate. `APPLE-GOLD-063`, a verification-code SMS failure, and `APPLE-GOLD-064`, an Apple ID recovery case without email access, were both gold escalation `1` but predicted `0`.

The recorded hypothesis is that ordinary troubleshooting language is overweighted relative to account recovery and security constraints. The recorded mitigation is recall-focused development and conservative review gates for high-risk patterns.

## 4. Historical grounding can introduce irrelevant or unsupported reply content

RAG received judge mean groundedness `4.38` versus NO_RAG `1.86`, but human/judge groundedness agreement was negative: weighted kappa `-0.1452` and Spearman `-0.1364`. For `APPLE-GOLD-232`, the RAG response introduced “iCloud Photo Library” into an Apple Store wait-time complaint; human overall was `2`, while the judge gave overall `4` and groundedness `5`. For `APPLE-GOLD-184`, humans scored groundedness `3` and overall `3` for the unsupported “iTunes Store team” routing claim, while the judge gave groundedness `5` and overall `4`.

The recorded hypothesis is that TF-IDF similarity and same-intent preference are not entailment checks. The recorded mitigation is evidence entailment validation and human groundedness review.

## 5. LLM-judge scores are not a reliable human-quality substitute

Across 40 matched rows, overall kappa was `0.1228`, groundedness kappa was `-0.1452`, relevance kappa was `0.2569`, and tone kappa was `0.0`. `APPLE-GOLD-163` RAG received human overall `2` but judge overall `4`; the reply incorrectly said the iPhone was “still going strong.” `APPLE-GOLD-025` RAG received human overall `4` and judge overall `5`.

The recorded hypothesis is that the judge rewards fluent support style and historical-looking evidence while humans notice message-specific misreadings. The recorded mitigation is blinded human acceptance review and multiple judges or adjudication for important releases.

# 4. What is misleading about my headline number?

The detailed caveat analysis is preserved in [analysis/headline_number_caveats.md](../analysis/headline_number_caveats.md).

The headline intent accuracy of `0.524` hides uneven class performance. Connectivity recall was `0.20`, device hardware recall was `0.3462`, orders/repair recall was `0.35`, and `OTHER_OR_AMBIGUOUS` F1 was `0.2899`. The 250-example golden set has uneven support, from `9` billing examples to `62` iOS/software examples, so accuracy is not a uniform risk estimate.

The labels are a judgment layer: the frozen single-intent taxonomy and primary-intent rule force a choice when customers describe several issues. The simple baseline uses `2,700` weak/silver rule-labeled training rows, not human-labeled training data. That limitation matters, but the comparison remains important: Llama 3.2 underperformed TF-IDF + Logistic Regression, which reached `0.624` accuracy and `0.5647142` macro F1.

Escalation accuracy of `0.812` is particularly misleading because the set is imbalanced (`195` non-escalations versus `55` escalations). The `70.91%` false-negative rate and `39` missed escalation cases matter more than the accuracy headline.

RAG’s judge mean overall of `4.16` versus NO_RAG `3.78` is not definitive because judge-human agreement was low: overall kappa `0.1228`, groundedness kappa `-0.1452`, relevance kappa `0.2569`, and tone kappa `0.0`. Historical TWCS AppleSupport responses may contain outdated policies, links, product versions, or routing practices. Finally, the average TF-IDF retrieval similarity of `0.2904473` measures lexical similarity, not answer quality or factual support.

# 5. One more week

The following is a proposed plan, not work already completed:

1. **Build a separate escalation development set.** Keep the 250 escalation gold examples held out. Sample and manually label a development set with extra coverage for account recovery, verification, fraud, data recovery, physical defects, and unresolved prior support.
2. **Improve escalation recall first.** Audit all 39 false negatives, add conservative high-risk features or routing gates, tune the decision threshold on development data, and report recall/FNR before accuracy.
3. **Strengthen intent classification.** Train a supervised model on a larger, cleaner human-labeled development set, compare against the existing weak-label baseline, and calibrate confidence on held-out data.
4. **Improve retrieval and reranking.** Add semantic candidate retrieval or a cross-encoder/reranker, retain same-intent preference as a feature rather than a guarantee, and evaluate evidence relevance separately from lexical similarity.
5. **Expand human reply evaluation.** Review more than the current 40 human-rated replies, balance issue types, and adjudicate disagreements on groundedness and customer-specific relevance.
6. **Calibrate the judge.** Use multiple blinded judges, compare judge outputs with human adjudication, and avoid treating a single LLM judge as a quality oracle.
7. **Handle historical-policy drift.** Timestamp historical evidence, detect obsolete links and product/version references, and add a policy freshness or abstention check before using a historical response in a draft.
8. **Broaden brands only if time permits.** After Apple-specific failure modes are addressed, test the architecture on another support brand with a separately defined taxonomy and held-out evaluation.
