# What Is Misleading About My Headline Number?

The headline numbers are useful checkpoints, but each compresses important limitations. The honest interpretation is not “the system works at X%.” It is “this system achieved X on this dataset, under this labeling scheme, with these known risks.”

## Intent accuracy hides uneven class performance

The Ollama intent classifier achieved accuracy `0.524` and macro F1 `0.5159378` on `250` golden examples. That result is not uniform across the frozen classes:

- Connectivity (`7`) recall was only `0.20`.
- Device hardware (`1`) recall was `0.3462`.
- Orders/repair (`8`) recall was `0.35`.
- `OTHER_OR_AMBIGUOUS` F1 was `0.2899`.
- Billing (`6`) recall was `1.0`, but it had only `9` examples.

The golden set is also imbalanced by intent: support ranges from `9` examples for class `6` to `62` for class `2`. A single accuracy number therefore does not describe the risk of each class. Macro metrics help, but they are still estimates from a small reviewed sample.

## The 250-example evaluation is valuable but small

The 250-row golden set is large enough to expose concrete failures, but it is not a full production workload. Sampling, wording, issue mix, and temporal characteristics affect the result. The intent score should be treated as an assignment checkpoint, not a stable estimate for every future Apple-support message.

## Human intent labels are a judgment layer

The taxonomy requires one primary intent even when a tweet contains multiple issues. The project explicitly applies a primary-reason rule and preserves `OTHER_OR_AMBIGUOUS`; this makes evaluation possible but introduces subjectivity at the boundary between, for example, battery hardware, iOS behavior, connectivity, and billing. The labels are reviewed labels, not an objective physical measurement of intent.

## The simple baseline uses weak/silver labels

The TF-IDF + Logistic Regression baseline trained on `2,700` weak/silver rows, not human-labeled training data. Those rows were created with transparent keyword rules, 300 per frozen class, and excluded golden IDs. Its result was accuracy `0.624` and macro F1 `0.5647142`.

That weak-label limitation does not invalidate the comparison, but it means the baseline is not a perfect oracle. It is still important that the LLM classifier underperformed it on this evaluation: Ollama accuracy was `0.524` and macro F1 `0.5159378`. The LLM should not be described as automatically superior because it is an LLM.

## Escalation accuracy is especially misleading

The escalation predictor achieved accuracy `0.812`, which sounds strong until the class distribution and error direction are shown. There were `195` non-escalation examples and `55` escalation examples. The confusion matrix was:

```text
[[187, 8],
 [39, 16]]
```

Recall was only `0.2909`, and the false-negative rate was `0.7091` (`70.91%`). The system missed `39` cases that human review marked for escalation. For this task, that miss rate matters more than the headline accuracy.

## Reply quality results depend on an imperfect judge

On the 50-example reply experiment, the LLM judge reported:

- NO_RAG mean overall: `3.78`
- RAG mean overall: `4.16`
- RAG higher: `18` examples
- NO_RAG higher: `0`
- Tied: `32`
- Average RAG-minus-NO_RAG difference: `0.38`

Those are judge outputs, not ground truth. In 40 human-reviewed rows, judge-human agreement was low for overall quality: weighted Cohen’s kappa `0.1228`. Groundedness agreement was negative at `-0.1452`, and tone kappa was `0.0`; tone Spearman correlation was undefined because one series was constant.

The headline RAG improvement therefore describes what this judge preferred in this sample. It does not establish that RAG replies are better for customers.

## Historical evidence is not automatically current policy

The retrieval corpus is reconstructed from historical TWCS AppleSupport interactions, including old device and iOS-era support conversations. Historical responses can contain old links, old product versions, old routing practices, or wording that is no longer appropriate. A retrieved response is evidence of past handling, not a current policy guarantee.

## Similarity is not answer quality

The reply experiment retrieved `3` cases per example, `150` cases total, with average TF-IDF similarity `0.2904473`. That number measures lexical retrieval similarity only. It does not prove that the retrieved support response is relevant, factually current, or sufficient to justify a generated claim.

This limitation appeared directly in human review. For `APPLE-GOLD-232`, the RAG reply introduced “iCloud Photo Library” into an Apple Store wait-time complaint; the human overall score was `2`, while the judge gave overall `4`. Retrieval can make a reply sound historically grounded while still steering it toward an irrelevant case.

## Bottom line

The most defensible headline is a set of conditional results: TF-IDF + Logistic Regression reached `0.624` accuracy on the 250-row intent set, Ollama reached `0.524`, RAG received a judge mean overall of `4.16` on a 50-example ablation, and escalation accuracy was `0.812` but missed `70.91%` of gold escalations. None of these numbers alone establishes production quality, current-policy correctness, or safe automated escalation.