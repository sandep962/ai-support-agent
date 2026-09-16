# Baseline training data

`silver_train.csv` is a **WEAK/SILVER-labeled** training dataset, not a human-labeled dataset. It contains 2,700 unique original-text Apple customer tweets: 300 examples for each frozen taxonomy class `1`–`8` and 300 `OTHER_OR_AMBIGUOUS` examples.

## Population and leakage control

Apple customer tweets are inbound TWCS tweets that are direct parents of outbound `AppleSupport` replies. Every `customer_tweet_id` in `evaluation/golden_set.csv` is excluded before sampling. The golden set is not used to create rules, select examples, retrieve nearest neighbors, train, or tune a model.

## Weak-label method

Labels use only transparent keyword/phrase rules on original customer text. A message gets classes 1–8 only when exactly one intent rule group matches. Text matching zero or multiple groups is `OTHER_OR_AMBIGUOUS`; historical AppleSupport reply text is never used. Exact normalized duplicate texts are removed before deterministic sampling.

Frozen taxonomy: `1` Device hardware / charging / physical functionality; `2` iOS and software behavior / updates; `3` Apple ID and account access; `4` iCloud, backup, restore, and data sync; `5` Apps / App Store / media downloads; `6` Billing, payments, subscriptions, refunds; `7` Connectivity: Wi-Fi / Bluetooth / cellular / calls; `8` Orders, repair, replacement, store, delivery; `OTHER_OR_AMBIGUOUS` unclear/insufficient information.
