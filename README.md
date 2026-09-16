# Hiver Support Agent

An evaluated AI customer-support agent built for the Hiver SDE Intern take-home assignment.

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

I started with the **Customer Support on Twitter (TWCS)** dataset and selected **Apple Support** as the target brand.

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

I created a **250-example reviewed golden set** for evaluation.

The golden examples are kept separate from the conventional training data and from historical retrieval so that the evaluation does not directly leak test examples into the system.

The golden set is stored in:

`evaluation/golden_set.csv`

### Step 5 — Baselines

Before evaluating the LLM classifier, I established two baselines:

- a trivial majority-class baseline;
- TF-IDF + Logistic Regression trained on 2,700 non-golden weak/silver-labelled examples.

This provides a simple reference point for determining whether the LLM actually adds value.

### Step 6 — LLM intent classifier

I evaluated a local **Llama 3.2** classifier against the same 250-example golden set.

The LLM result was not assumed to be better simply because it was more sophisticated.

In fact, the Llama classifier performed below the TF-IDF + Logistic Regression baseline on the headline intent metrics. That result is retained as-is and forms part of the failure analysis.

### Step 7 — Historically grounded reply generation

For reply generation, I ran a controlled experiment using the same Llama 3.2 model:

- **NO_RAG:** customer message + predicted intent;
- **RAG:** customer message + predicted intent + three retrieved historical customer → support cases.

The historical cases were retrieved using TF-IDF similarity, with preference for cases matching the predicted intent when available.

The experiment was run on 50 deterministic golden examples.

This makes the RAG comparison an ablation rather than a comparison between unrelated systems.

### Step 8 — LLM reply judge

The 50-example reply experiment was evaluated using an independent LLM judge.

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

I did not treat the LLM judge as ground truth.

A separate 40-reply sample was manually evaluated and compared against the LLM judge using weighted Cohen's kappa and Spearman correlation.

The agreement results are stored in:

`results/judge_human_agreement.json`

The agreement was limited, particularly for groundedness, so the judge is treated as a supporting evaluation signal rather than a replacement for human evaluation.

### Step 10 — Escalation evaluation

I manually labeled all 250 golden examples for whether the issue reasonably required human escalation.

The escalation model was then evaluated against those labels.

The resulting analysis showed that escalation accuracy alone was misleading because the system missed many cases that should have been escalated. The false-negative rate is therefore explicitly reported.

---

## 3. Architecture

```text
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
| Predictor            |
+----------------------+
     |
     v
escalate + reason


Final structured result
-----------------------
intent
confidence
draft_reply
escalate
escalation_reason
evidence_ids
