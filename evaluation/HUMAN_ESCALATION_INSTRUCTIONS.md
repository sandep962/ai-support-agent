# Human Escalation Labeling Instructions

Review the actual customer message and decide whether an automated support response should handle it or whether it should be escalated to a human.

Enter:

- `escalate_gold = 1` when the issue reasonably requires human intervention, account-specific action, sensitive or security handling, transaction investigation, fraud or unauthorized-activity handling, serious data-loss or recovery handling, physical repair or service intervention, legal or other high-risk handling, or when the customer explicitly requires human support after normal assistance.
- `escalate_gold = 0` for routine informational questions and routine troubleshooting that can reasonably be handled through an automated support response.

Do not infer escalation from the intent label alone. Judge the actual customer message. If uncertain, use the safest reasonable interpretation and briefly explain the decision in `escalation_reason`.

For every row, enter only `0` or `1` in `escalate_gold` and add a concise explanation in `escalation_reason`. Do not change `example_id`, `customer_tweet_id`, `customer_text`, or `intent`.
