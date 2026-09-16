# Human Reply Evaluation Instructions

Evaluate each reply independently. Do not consult or infer the LLM-judge scores. Score the reply using only the customer message and, for RAG rows, the historical evidence available with that reply.

Use integer scores from 1 to 5:

- **Relevance:** Does the reply directly address the customer's issue?
- **Groundedness:** Are the reply's factual claims and suggested actions supported by the available evidence or historical cases? For NO_RAG, use the customer message alone and penalize unsupported claims.
- **Tone:** Is the response appropriate, concise, professional, and empathetic for customer support?
- **Overall:** What is the overall usefulness and quality of the reply as a customer-support draft?

Enter one integer from 1 through 5 in each `human_relevance`, `human_groundedness`, `human_tone`, and `human_overall` field. Use `human_notes` for brief evidence-based comments when useful.

Review NO_RAG and RAG rows independently. Do not compare paired replies while scoring, and do not use gold intents, predicted intents, or any LLM-judge score to determine ratings.
