# Hiver Support Agent

An evaluated AI customer-support agent built for the Hiver **SDE** Intern take-home assignment.

The system uses Apple Support as the target brand and is designed around three tasks:

1. **Intent classification** — classify an incoming customer message into a small, fixed taxonomy of support intents.
2. **Historically grounded reply generation** — retrieve similar Apple customer-support interactions and use them as evidence when drafting a response.
3. **Escalation** — decide whether the issue can be handled automatically or should be sent to a human, with a reason.

The project focuses on **evaluation, reproducibility, and failure analysis**, not just building a demo.

---

## 1. Problem framing

The goal is not to build a production-ready customer-support platform. The goal is to determine whether a lightweight AI support agent can reliably perform three support tasks on noisy real-world customer messages.

For this project, a good system should:

- identify the customer's primary support intent;
- produce a relevant response grounded in how the brand historically handled similar cases;
- avoid inventing policies, guarantees, or unsupported troubleshooting steps;
- escalate issues that reasonably require human intervention;
- provide measurable evidence of where the system works and where it fails.

The project deliberately does **not** include a frontend, authentication system, deployment infrastructure, production policy engine, or production customer-data integrations.

---

## 2. How I built this

The project was developed as a sequence of measurable components rather than starting with a final chatbot.

### Step 1 — Dataset inspection

I started with the **Customer Support on Twitter (**TWCS**)** dataset and selected **Apple Support** as the target brand.

The dataset contains customer tweets, support responses, timestamps, and response-link fields. These links were used to reconstruct customer → support interactions.

The repository records the dataset inspection in:

`results/dataset_inspection.md`

### Step 2 — Historical support corpus

Apple Support conversations were reconstructed into customer → support pairs.

These historical interactions form the evidence corpus used by the reply-generation experiment.

The derived Apple Support analysis artifacts are stored under:

`results/apple_support/`

The full reconstructed corpus is intentionally not committed to Git because it is a large derived dataset. The source dataset should be obtained according to its original provider's terms.

### Step 3 — Frozen intent taxonomy

I defined a small taxonomy from the Apple Support data and froze it before evaluation.

The system uses eight intents plus `OTHER_OR_AMBIGUOUS`:

| ID | Intent |
|---|---|
| 1 | Device hardware / charging / physical functionality |
| 2 | iOS and software behavior / updates |
| 3 | Apple ID and account access |
| 4 | iCloud, backup, restore, and data sync |
| 5 | Apps / App Store / media downloads |
| 6 | Billing, payments, subscriptions, refunds |
| 7 | Connectivity: Wi-Fi / Bluetooth / cellular / calls |
| 8 | Orders, repair, replacement, store, delivery |
| OTHER_OR_AMBIGUOUS | Insufficient or unclear information |

For messages containing multiple issues, the label represents the customer's **primary reason for seeking support**.

### Step 4 — Held-out golden evaluation set

I created a ****250**-example reviewed golden set** for evaluation.

The golden examples are kept separate from the conventional training data and from historical retrieval so that the evaluation does not directly leak test examples into the system.

The golden set is stored in:

`evaluation/golden_set.csv`

### Step 5 — Baselines

Before evaluating the **LLM** classifier, I established two baselines:

- a trivial majority-class baseline;
- TF-**IDF** + Logistic Regression trained on 2,**700** non-golden weak/silver-labelled examples.

This provides a simple reference point for determining whether the **LLM** actually adds value.

### Step 6 — LLM intent classifier

I evaluated a local **Llama 3.2** classifier against the same **250**-example golden set.

The **LLM** result was not assumed to be better simply because it was more sophisticated.

In fact, the Llama classifier performed below the TF-**IDF** + Logistic Regression baseline on the headline intent metrics. That result is retained as-is and forms part of the failure analysis.

### Step 7 — Historically grounded reply generation

For reply generation, I ran a controlled experiment using the same Llama 3.2 model:

- **NO_RAG:** customer message + predicted intent;
- ****RAG**:** customer message + predicted intent + three retrieved historical customer → support cases.

The historical cases were retrieved using TF-**IDF** similarity, with preference for cases matching the predicted intent when available.

The experiment was run on 50 deterministic golden examples.

This makes the **RAG** comparison an ablation rather than a comparison between unrelated systems.

### Step 8 — LLM reply judge

The 50-example reply experiment was evaluated using an independent **LLM** judge.

Each reply was scored on:

- relevance;
- groundedness;
- tone;
- overall quality.

The judge scores are stored in:

`results/reply_judge_scores.csv`

and

`results/reply_judge_results.json`

### Step 9 — Human agreement check

I did not treat the **LLM** judge as ground truth.

A separate 40-reply sample was manually evaluated and compared against the **LLM** judge using weighted Cohen's kappa and Spearman correlation.

The agreement results are stored in:

`results/judge_human_agreement.json`

The agreement was limited, particularly for groundedness, so the judge is treated as a supporting evaluation signal rather than a replacement for human evaluation.

### Step 10 — Escalation evaluation

I manually labeled all **250** golden examples for whether the issue reasonably required human escalation.

The escalation model was then evaluated against those labels.

The resulting analysis showed that escalation accuracy alone was misleading because the system missed many cases that should have been escalated. The false-negative rate is therefore explicitly reported.

---

## 3. Architecture

    customer_text
    |
    v
    +----------------------+
    | Llama 3.2 Intent     |
    | Classifier            |
    +----------------------+
    |
    v
    predicted intent
    |
    v
    +----------------------+
    | TF-IDF Historical    |
    | Retrieval            |
    +----------------------+
    |
    top 3 historical cases
    |
    v
    +----------------------+
    | Llama 3.2 Reply      |
    | Generator            |
    +----------------------+
    |
    v
    draft_reply

customer_text
|
v
+----------------------+
| Llama 3.2 Escalation |
| Predictor |
+----------------------+
|
v
escalate + reason

**Final structured result:**

intent confidence draft_reply escalate escalation_reason evidence_ids

The final one-message interface is:

`src.pipeline.SupportAgentPipeline`

---

## 4. Evaluation methodology

The evaluation is deliberately component-based.

### Intent classification

Metrics:

- Accuracy
- Macro Precision
- Macro Recall
- Macro F1
- Per-class precision/recall/F1
- Confusion matrix

The conventional baseline uses only the 2,**700** non-golden weak/silver-labelled training examples.

### Reply generation

The same Llama 3.2 model is evaluated under two conditions:

**NO_RAG** — customer message + predicted intent

versus

**RAG** — customer message + predicted intent + 3 historical cases

This isolates the effect of historical grounding.

### Escalation

Metrics:

- Accuracy
- Precision
- Recall
- F1
- False positives
- False negatives
- False-negative rate

Recall and false-negative rate are emphasized because incorrectly auto-handling an issue that should reach a human is the more important failure mode for this experiment.

---

## 5. Headline results

| System | Metric | Result |
|---|---|---|
| Majority intent | Accuracy | 0.248 |
| Majority intent | Macro F1 | 0.0442 |
| TF-IDF + Logistic Regression | Accuracy | 0.624 |
| TF-IDF + Logistic Regression | Macro F1 | 0.5647 |
| Llama 3.2 intent | Accuracy | 0.524 |
| Llama 3.2 intent | Macro F1 | 0.5159 |
| NO_RAG reply | Mean overall judge score | 3.78 / 5 |
| RAG reply | Mean overall judge score | 4.16 / 5 |
| Escalation | Accuracy | 0.812 |
| Escalation | Recall | 0.2909 |
| Escalation | False-negative rate | 0.7091 |

### What these results show

The Llama 3.2 intent classifier did not outperform the simple TF-**IDF** + Logistic Regression baseline.

For reply generation, the **RAG** condition received a higher mean overall judge score than NO_RAG:

**4.16 vs 3.78**

The largest difference was in judged groundedness, suggesting that historical examples provided useful grounding. However, this was a 50-example experiment and the human-agreement results show that the **LLM** judge is imperfect.

The escalation component achieved 0.**812** accuracy but only 0.**2909** recall, with a 0.**7091** false-negative rate. Therefore, the accuracy number by itself would give a misleading impression of escalation performance.

---

## 6. What is misleading about my headline number?

The headline numbers should not be interpreted as proof that this is a production-ready support agent.

Several factors make the numbers narrower than they may initially appear:

- The intent evaluation contains only **250** reviewed examples.
- Intent classes are unevenly represented.
- The conventional baseline uses weak/silver labels rather than a fully human-labelled training set.
- The **LLM** classifier underperforms the simple TF-**IDF** baseline.
- The **RAG** reply experiment contains only 50 examples.
- The reply judge is an **LLM** and showed limited agreement with human ratings.
- Historical support responses may contain outdated products, links, policies, or routing guidance.
- TF-**IDF** retrieval measures textual similarity; it does not guarantee that the retrieved response supports every generated claim.
- Escalation has a 70.91% false-negative rate.
- The experiments are based on Apple Support and are not evidence that the system generalizes to other brands.

The purpose of the evaluation is therefore not to present one impressive number. It is to expose where the system succeeds, where it fails, and which components require further work.

---

## 7. Top failure modes

Detailed failure analyses are available under `analysis/`.

**1. Intent confusion between closely related support issues**

Hardware, software, charging, account, and connectivity messages can contain overlapping language. This causes the classifier to confuse semantically related intents.

**2. High-confidence incorrect intent predictions**

The **LLM** often produced high confidence even when its prediction was wrong. This means raw confidence cannot currently be treated as a reliable safety signal.

**3. Weak handling of ambiguous messages**

Short or underspecified customer messages are difficult to map reliably to one taxonomy category. `OTHER_OR_AMBIGUOUS` is therefore necessary, but the classifier also overused it in several error cases.

**4. Historical retrieval does not guarantee factual grounding**

A retrieved historical response may be textually similar without being sufficient evidence for every claim in a new response. Retrieval quality and evidence quality therefore need to be evaluated separately.

**5. Escalation misses high-risk cases**

The escalation model produced relatively few false positives but missed 39 of 55 human-escalation cases in the **250**-example evaluation. This resulted in:

- Recall: 0.**2909**
- False-negative rate: 0.**7091**

This is the most important limitation of the current escalation component.

Detailed examples and hypotheses are documented in:

`analysis/escalation_failure_analysis.md`

and

`analysis/final_failure_analysis.md`

---

## 8. Repository structure

**HIVER**/ ├── **README**.md ├── requirements.txt │ ├── src/ │ ├── ai_intent_classifier.py │ ├── escalation.py │ ├── pipeline.py │ ├── reply_generator.py │ └── retrieval.py │ ├── baselines/ │ ├── majority.py │ └── tfidf_logistic.py │ ├── data/ │ ├── **README**.md │ └── silver_train.csv │ ├── evaluation/ │ ├── golden_set.csv │ ├── escalation_labeling.csv │ ├── human_reply_evaluation.csv │ ├── HUMAN_EVALUATION_INSTRUCTIONS.md │ ├── HUMAN_ESCALATION_INSTRUCTIONS.md │ ├── evaluate_ai_classifier.py │ ├── evaluate_escalation.py │ ├── evaluate_replies.py │ ├── evaluate_reply_quality.py │ ├── calculate_judge_human_agreement.py │ └── reply_judge.py │ ├── results/ │ ├── ai_classifier_predictions.csv │ ├── ai_classifier_results.json │ ├── escalation_predictions.csv │ ├── escalation_results.json │ ├── judge_human_agreement.json │ ├── majority_intent.json │ ├── reply_judge_results.json │ ├── reply_judge_scores.csv │ ├── reply_predictions.csv │ ├── reply_results.json │ ├── tfidf_logistic_intent.json │ └── apple_support/ │ ├── analysis/ │ ├── ai_classifier_failure_analysis.md │ ├── escalation_failure_analysis.md │ ├── final_failure_analysis.md │ ├── headline_number_caveats.md │ └── decision_log.md │ └── report/ └── report.md

---

## 9. Dataset source and citation

The project uses the Customer Support on Twitter (**TWCS**) dataset.

The source data was inspected from `twcs.csv`.

The repository inspection recorded approximately 2.81 million rows and the original tweet fields, including:

- `tweet_id`
- `author_id`
- `inbound`
- `created_at`
- `text`
- `response_tweet_id`
- `in_response_to_tweet_id`

Apple Support outbound messages were linked to their inbound customer parents to construct historical customer → support pairs.

The dataset source should be obtained from its original provider:

[https://[www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter))

The original dataset's licensing and redistribution terms apply. The full source dataset is not included in this repository.

---

## 10. Dataset and leakage controls

The evaluation was designed to avoid direct test leakage.

- Golden customer examples are excluded from training.
- Golden customer IDs are excluded from retrieval.
- Reconstructed conversations containing golden customer examples are excluded from retrieval.
- The conventional classifier trains only on non-golden silver data.
- The reply experiment uses historical cases separate from the golden examples.
- The **LLM** judge does not receive the gold intent labels.
- The reply judge evaluates NO_RAG and **RAG** independently.

The full reconstructed historical corpus is intentionally excluded from Git because it is a large derived dataset.

---

## 11. Environment and setup

Run commands from the repository root.

Install dependencies:

```bash python -m pip install scikit-learn pandas scipy ```

The Llama integration uses the local Ollama **HTTP** **API** through Python's standard-library **HTTP** client.

No OpenAI **API** key is required.

---

## 12. Ollama / Llama 3.2 setup

Install Ollama and download the model:

```bash ollama pull llama3.2 ```

The default configuration is:

OLLAMA_HOST=[http://localhost:**11434**](http://localhost:**11434**) OLLAMA_MODEL=llama3.2

These can be overridden with environment variables when required.

---

## 13. Run the pipeline

Run the pipeline's three-message smoke test:

```bash python src/pipeline.py ```

Or run the agent against one message:

```bash python -c "from src.pipeline import SupportAgentPipeline; import json; print(json.dumps(SupportAgentPipeline().predict('My iPhone keeps freezing after the latest iOS update.'), indent=2))" ```

The output contains:

intent confidence draft_reply escalate escalation_reason evidence_ids

The pipeline performs:

Intent classification ↓ Historical retrieval ↓ Grounded reply generation ↓ Escalation prediction ↓ Structured output validation

---

## 14. Reproduce intent evaluation

The saved results under `results/` are completed evaluation artifacts.

To rerun the Llama classifier against the held-out **250**-example golden set:

```bash python evaluation/evaluate_ai_classifier.py ```

This performs **250** local Ollama calls.

The simple baselines can be rerun with:

```bash python baselines/majority.py --golden evaluation/golden_set.csv python baselines/tfidf_logistic.py --train data/silver_train.csv --golden evaluation/golden_set.csv ```

---

## 15. Reproduce reply / RAG evaluation

Run the controlled 50-example reply experiment:

```bash python evaluation/evaluate_replies.py ```

This generates:

- 50 NO_RAG replies;
- 50 **RAG** replies;
- 3 retrieved historical cases per **RAG** example.

Then run the **LLM** judge:

```bash python evaluation/evaluate_reply_quality.py ```

The human evaluation sample is already completed and stored in:

`evaluation/human_reply_evaluation.csv`

---

## 16. Reproduce escalation evaluation

Run:

```bash python evaluation/evaluate_escalation.py ```

The evaluator reads the customer messages, generates escalation predictions using Llama 3.2, and compares them with the manually reviewed `escalate_gold` labels.

The completed results are stored under:

results/escalation_predictions.csv results/escalation_results.json

---

## 17. Failure analysis

The project includes detailed analysis artifacts:

- `analysis/ai_classifier_failure_analysis.md`
- `analysis/escalation_failure_analysis.md`
- `analysis/final_failure_analysis.md`
- `analysis/headline_number_caveats.md`
- `analysis/decision_log.md`

The failure analysis contains representative incorrect predictions, confusion patterns, hypotheses, and limitations.

The decision log records non-obvious engineering decisions, alternatives considered, and evidence/trade-offs.

---

## 18. One more week

With another week, I would focus on reliability rather than adding a frontend.

**1. Improve escalation recall**

The current escalation false-negative rate is too high. I would:

- introduce explicit risk features;
- separate routine support from account/security and transaction-sensitive cases;
- tune the escalation threshold;
- evaluate the trade-off between false positives and false negatives.

**2. Improve intent classification**

The Llama classifier currently underperforms the TF-**IDF** baseline. I would investigate:

- few-shot intent examples;
- confidence calibration;
- intent-specific prompts;
- a stronger supervised classifier;
- better handling of ambiguous and multi-issue messages.

**3. Improve retrieval**

I would compare TF-**IDF** retrieval with embedding-based retrieval and evaluate:

- retrieval relevance;
- same-intent retrieval rate;
- evidence usefulness;
- duplicate/near-duplicate cases.

**4. Strengthen grounding evaluation**

Instead of relying primarily on an **LLM** judge, I would create a larger human-labelled reply evaluation set with explicit claim-level grounding checks.

**5. Validate across another brand**

The current results are Apple-specific. A second support brand would test whether the methodology generalizes beyond the selected dataset slice.

---

## 19. Limitations

- The intent golden set contains **250** reviewed examples.
- Intent classes are unevenly represented.
- Conventional baseline training labels are weak/silver labels.
- Historical responses may contain outdated information.
- TF-**IDF** similarity does not guarantee factual support.
- Reply evaluation uses only 50 examples.
- The **LLM** judge showed limited agreement with human ratings.
- Escalation has a high false-negative rate.
- The system has not been validated across multiple brands.
- The full historical corpus is not included in the repository.

---

## 20. Decision log

The non-obvious engineering decisions are documented in:

`analysis/decision_log.md`

Examples include:

- why Apple Support was selected;
- why the taxonomy was frozen;
- why a golden set was kept separate;
- why TF-**IDF** was used as the first retrieval method;
- why **RAG** was evaluated as an ablation;
- why Llama was run locally;
- why escalation recall was emphasized;
- why the full historical corpus was not committed;
- why the **LLM** judge was checked against human ratings.

---

## 21. Key takeaway

The main result of this project is not that an **LLM** solved customer support.

The evaluation shows a more useful picture:

- a simple TF-**IDF** classifier outperformed the Llama intent classifier;
- historical retrieval improved the judged reply score in the controlled **RAG** experiment;
- the strongest **RAG** effect was on judged groundedness;
- the **LLM** judge showed limited agreement with human ratings;
- escalation accuracy looked reasonable until false-negative rate was examined;
- the escalation component missed many cases that should have reached a human.

The system therefore demonstrates both working support-agent components and measurable failure modes, with the evaluation artifacts and analysis available in the repository.
