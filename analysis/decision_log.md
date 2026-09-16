# Engineering Decision Log

## 1. Frozen taxonomy with `OTHER_OR_AMBIGUOUS`

**Decision:** Use the frozen eight intents plus `OTHER_OR_AMBIGUOUS`.

**Why:** The assignment requires a stable intent contract for comparison across baselines, Ollama classification, retrieval, and escalation.

**Alternative considered:** Add, merge, or rename intents based on exploratory dataset themes.

**Evidence/trade-off:** The completed classifier results use nine labels and preserve the taxonomy. This improves comparability but forces difficult multi-issue messages into one primary label or the ambiguity class.

## 2. Primary-intent rule for multi-issue tweets

**Decision:** For multi-issue tweets, select the primary reason the customer needs support.

**Why:** The classifier emits one intent, while real customer tweets often contain battery, update, call, and account cues together.

**Alternative considered:** Emit multiple intents or alter the taxonomy.

**Evidence/trade-off:** The classifier instructions explicitly apply the primary-reason rule. It preserves the frozen interface but contributes to observed confusion on messages such as `APPLE-GOLD-002`.

## 3. Preserve raw customer text

**Decision:** Preserve original customer text in golden, training, retrieval, prediction, and review artifacts.

**Why:** Original wording, abbreviations, URLs, and noisy phrasing are part of the support problem and allow auditability.

**Alternative considered:** Normalize or rewrite messages before storage.

**Evidence/trade-off:** The pair corpus and prediction CSVs retain original text. This supports reproducibility but leaves the models exposed to spelling, profanity, HTML entities, and incomplete messages.

## 4. Reconstruct customer-to-Apple support pairs

**Decision:** Build historical cases from inbound customer parents and corresponding outbound `AppleSupport` replies, including conversation components.

**Why:** Reply generation must be grounded in how Apple historically handled similar customer issues, not in arbitrary tweets.

**Alternative considered:** Retrieve from all tweets or use only customer text without support responses.

**Evidence/trade-off:** The repository contains `106,646` validated customer-to-support edges and `84,333` reconstructed components. Pair reconstruction provides response evidence but inherits the source’s historical noise and thread complexity.

## 5. Keep the golden set held out

**Decision:** Never use the 250 golden examples for training, retrieval indexing, prompt examples, or tuning.

**Why:** Evaluation must measure generalization to reviewed examples.

**Alternative considered:** Use golden examples to improve prompts or retrieval because they are already labeled.

**Evidence/trade-off:** The silver-data documentation records zero golden/training ID overlap, and the retriever excludes golden customer IDs and their conversations. This protects evaluation validity at the cost of excluding potentially useful near-neighbor evidence.

## 6. Use weak/silver labels only for the simple baseline

**Decision:** Build `2,700` silver training rows with transparent rules and use them for the TF-IDF + Logistic Regression baseline.

**Why:** A reproducible non-LLM reference was needed without using human golden labels for fitting.

**Alternative considered:** Train the simple baseline on the reviewed golden labels or skip a conventional baseline.

**Evidence/trade-off:** The data README calls the labels weak/silver and documents 300 examples per class. This enables a fair baseline but introduces label noise.

## 7. Retain TF-IDF + Logistic Regression as a serious comparator

**Decision:** Compare Ollama intent classification with a CPU TF-IDF + Logistic Regression model.

**Why:** A simple lexical model tests whether an LLM adds value beyond a strong reproducible baseline.

**Alternative considered:** Compare only against the majority baseline.

**Evidence/trade-off:** TF-IDF + Logistic Regression reached accuracy `0.624` and macro F1 `0.5647142`, while Ollama reached `0.524` and `0.5159378`. The comparison exposed that the LLM was not automatically better.

## 8. Use local Ollama `llama3.2`

**Decision:** Use the local Ollama server and configurable `OLLAMA_MODEL`, defaulting to `llama3.2`.

**Why:** The project needed a runnable local model without requiring an OpenAI credential.

**Alternative considered:** Continue using the invalid OpenAI configuration or add a hosted provider.

**Evidence/trade-off:** Ollama was installed locally with `llama3.2`; all classifier, reply, judge, and escalation experiments ran against it. This removes API-key dependence but makes results dependent on one local model/version.

## 9. Use TF-IDF retrieval with same-intent preference

**Decision:** Retrieve the top three historical cases with TF-IDF cosine similarity and prefer cases whose transparent cue-based retrieval intent matches the predicted intent.

**Why:** The assignment required a lightweight CPU-reproducible retriever and intent-aware retrieval.

**Alternative considered:** Use embeddings, a hosted vector database, or retrieve arbitrary support tweets.

**Evidence/trade-off:** The experiment retrieved 150 cases for 50 examples with average similarity `0.2904473`; same-intent cases were available for all 50. The approach is simple and reproducible, but similarity does not establish factual support.

## 10. Run a no-RAG versus RAG ablation

**Decision:** Generate both a no-RAG and a historically grounded reply for the same 50 deterministic examples.

**Why:** This isolates the effect of historical evidence before making any quality claim.

**Alternative considered:** Evaluate only the RAG system.

**Evidence/trade-off:** The experiment produced 100 successful generations and preserved retrieved evidence IDs. It supports a controlled comparison but is a small subset rather than a full 250-example reply study.

## 11. Use an LLM judge with a four-dimension rubric

**Decision:** Score relevance, groundedness, tone, and overall quality from 1 to 5 using the same local model.

**Why:** The assignment requested an initial automated quality evaluation before broader human review.

**Alternative considered:** Use only fluency or only a single overall score.

**Evidence/trade-off:** The judge reported RAG overall mean `4.16` versus NO_RAG `3.78`, but this result was later qualified by human agreement checks.

## 12. Add a human agreement check before trusting judge comparisons

**Decision:** Compare the judge with 40 blinded human ratings using weighted Cohen’s kappa and Spearman correlation.

**Why:** Automated judges can reward plausible style while missing customer-specific errors.

**Alternative considered:** Treat judge scores as ground truth.

**Evidence/trade-off:** Agreement was low: overall kappa `0.1228`, groundedness kappa `-0.1452`, and tone kappa `0.0`. The check reduces overclaiming but requires manual review effort.

## 13. Emphasize escalation recall and false-negative rate

**Decision:** Report escalation recall and false-negative rate prominently, not accuracy alone.

**Why:** Missing a case that requires a human is more consequential than sending a routine case for review.

**Alternative considered:** Optimize or headline accuracy because the label distribution is mostly non-escalation.

**Evidence/trade-off:** Escalation accuracy was `0.812`, but recall was `0.2909` and false-negative rate was `0.7091`, with `39` false negatives. This better reflects the operational risk.

## 14. Keep productization outside this assignment phase

**Decision:** Do not build a frontend, API server, deployment system, authentication, RAG expansion, or reply-generation product workflow beyond the experiment.

**Why:** The assignment explicitly prioritized evaluation and evidence before productization.

**Alternative considered:** Add a user interface or deployment layer around the pipeline.

**Evidence/trade-off:** The completed work ends with a runnable one-message pipeline and saved evaluations. This keeps scope controlled but leaves operational concerns for a later phase.