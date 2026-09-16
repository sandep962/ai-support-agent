# TWCS dataset inspection

- Source inspected read-only: `D:\DOWNLOAD\archive\twcs\twcs.csv`
- Total rows: **2,811,774**
- No preprocessing, normalization, or text modification was performed.

## Schema and missing values

| Column | Read type | Missing values | Missing % |
|---|---|---:|---:|
| `tweet_id` | integer-like identifier (read as string to preserve IDs) | 0 | 0.00% |
| `author_id` | string identifier/account handle | 0 | 0.00% |
| `inbound` | boolean-like string (True/False) | 0 | 0.00% |
| `created_at` | string timestamp | 0 | 0.00% |
| `text` | string (original text preserved) | 0 | 0.00% |
| `response_tweet_id` | string containing one or more tweet IDs | 1,040,629 | 37.01% |
| `in_response_to_tweet_id` | string containing one or more tweet IDs | 794,335 | 28.25% |

## Inbound

- `inbound=True`: **1,537,843**
- `inbound=False`: **1,273,931**
- Other/missing inbound values: **0**

## Authors

- Unique `author_id` values: **702,777**

### Top 30 authors by tweet count

| Rank | Author | Tweets |
|---:|---|---:|
| 1 | `AmazonHelp` | 169,840 |
| 2 | `AppleSupport` | 106,860 |
| 3 | `Uber_Support` | 56,270 |
| 4 | `SpotifyCares` | 43,265 |
| 5 | `Delta` | 42,253 |
| 6 | `Tesco` | 38,573 |
| 7 | `AmericanAir` | 36,764 |
| 8 | `TMobileHelp` | 34,317 |
| 9 | `comcastcares` | 33,031 |
| 10 | `British_Airways` | 29,361 |
| 11 | `SouthwestAir` | 28,977 |
| 12 | `VirginTrains` | 27,817 |
| 13 | `Ask_Spectrum` | 25,860 |
| 14 | `XboxSupport` | 24,557 |
| 15 | `sprintcare` | 22,381 |
| 16 | `hulu_support` | 21,872 |
| 17 | `sainsburys` | 19,466 |
| 18 | `GWRHelp` | 19,364 |
| 19 | `AskPlayStation` | 19,098 |
| 20 | `ChipotleTweets` | 18,749 |
| 21 | `VerizonSupport` | 17,966 |
| 22 | `UPSHelp` | 17,817 |
| 23 | `ATVIAssist` | 17,650 |
| 24 | `O2` | 16,212 |
| 25 | `Safaricom_Care` | 16,077 |
| 26 | `idea_cares` | 15,724 |
| 27 | `AskTarget` | 13,218 |
| 28 | `AirAsiaSupport` | 12,829 |
| 29 | `BofA_Help` | 12,683 |
| 30 | `SW_Help` | 12,231 |

## Text (original text, unmodified)

- Average length: **113.89** characters
- Median length: **115** characters
- Minimum / maximum length: **1 / 513** characters

### First 20 CSV-order examples

1. Tweet `1` by `sprintcare`: @115712 I understand. I would like to assist you. We would need to get you into a private secured link to further assist.
2. Tweet `2` by `115712`: @sprintcare and how do you propose we do that
3. Tweet `3` by `115712`: @sprintcare I have sent several private messages and no one is responding as usual
4. Tweet `4` by `sprintcare`: @115712 Please send us a Private Message so that we can further assist you. Just click ‘Message’ at the top of your profile.
5. Tweet `5` by `115712`: @sprintcare I did.
6. Tweet `6` by `sprintcare`: @115712 Can you please send us a private message, so that I can gain further details about your account?
7. Tweet `8` by `115712`: @sprintcare is the worst customer service
8. Tweet `11` by `sprintcare`: @115713 This is saddening to hear. Please shoot us a DM, so that we can look into this for you. -KC
9. Tweet `12` by `115713`: @sprintcare You gonna magically change your connectivity for me and my whole family ? 🤥 💯
10. Tweet `15` by `sprintcare`: @115713 We understand your concerns and we'd like for you to please send us a Direct Message, so that we can further assist you. -AA
11. Tweet `16` by `115713`: @sprintcare Since I signed up with you....Since day 1
12. Tweet `17` by `sprintcare`: @115713 H there! We'd definitely like to work with you on this, how long have you been experiencing this issue? -AA
13. Tweet `18` by `115713`: @115714 y’all lie about your “great” connection. 5 bars LTE, still won’t load something. Smh.
14. Tweet `19` by `sprintcare`: @115715 Please send me a private message so that I can send you the link to access your account. -FR
15. Tweet `20` by `115715`: @115714 whenever I contact customer support, they tell me I have shortcode enabled on my account, but I have never in the 4 years I've tried https://t.co/0G98RtNxPK
16. Tweet `21` by `Ask_Spectrum`: @115716 What information is incorrect? ^JK
17. Tweet `22` by `115716`: @Ask_Spectrum Would you like me to email you a copy of one since Spectrum is not updating your training?
18. Tweet `25` by `Ask_Spectrum`: @115716 Our department is part of the corporate office.  If you're particular area has gone to this format, we were unawa... https://t.co/P7XCmTzPQj
19. Tweet `26` by `115716`: @Ask_Spectrum I received this from your corporate office would you like a copy?
20. Tweet `27` by `Ask_Spectrum`: @115716 No thank you. ^JK

## Conversation-link columns

- `response_tweet_id` missing: **1,040,629 (37.01%)**
- `in_response_to_tweet_id` missing: **794,335 (28.25%)**
- A `response_tweet_id` points forward to a reply/replies; `in_response_to_tweet_id` points to the parent tweet(s). IDs may be comma-separated.

### Link examples

- Tweet `1` (`sprintcare`, inbound=False) → response IDs `2`; parent IDs `3`. Text: @115712 I understand. I would like to assist you. We would need to get you into a private secured link to further assist.
- Tweet `2` (`115712`, inbound=True) → response IDs `—`; parent IDs `1`. Text: @sprintcare and how do you propose we do that
- Tweet `3` (`115712`, inbound=True) → response IDs `1`; parent IDs `4`. Text: @sprintcare I have sent several private messages and no one is responding as usual
- Tweet `4` (`sprintcare`, inbound=False) → response IDs `3`; parent IDs `5`. Text: @115712 Please send us a Private Message so that we can further assist you. Just click ‘Message’ at the top of your profile.
- Tweet `5` (`115712`, inbound=True) → response IDs `4`; parent IDs `6`. Text: @sprintcare I did.
- Tweet `6` (`sprintcare`, inbound=False) → response IDs `5,7`; parent IDs `8`. Text: @115712 Can you please send us a private message, so that I can gain further details about your account?
- Tweet `8` (`115712`, inbound=True) → response IDs `9,6,10`; parent IDs `—`. Text: @sprintcare is the worst customer service
- Tweet `11` (`sprintcare`, inbound=False) → response IDs `—`; parent IDs `12`. Text: @115713 This is saddening to hear. Please shoot us a DM, so that we can look into this for you. -KC
- Tweet `12` (`115713`, inbound=True) → response IDs `11,13,14`; parent IDs `15`. Text: @sprintcare You gonna magically change your connectivity for me and my whole family ? 🤥 💯
- Tweet `15` (`sprintcare`, inbound=False) → response IDs `12`; parent IDs `16`. Text: @115713 We understand your concerns and we'd like for you to please send us a Direct Message, so that we can further assist you. -AA
- Tweet `16` (`115713`, inbound=True) → response IDs `15`; parent IDs `17`. Text: @sprintcare Since I signed up with you....Since day 1
- Tweet `17` (`sprintcare`, inbound=False) → response IDs `16`; parent IDs `18`. Text: @115713 H there! We'd definitely like to work with you on this, how long have you been experiencing this issue? -AA

## Likely support brands/accounts: outbound activity

Outbound (`inbound=False`) authors are treated as likely support/brand accounts. `Unique parent IDs` comes from `in_response_to_tweet_id`. `Verified inbound parents` is the exact subset confirmed in a second read-only pass to be inbound customer tweets.

| Rank | Likely brand/account | Outbound tweets | Unique parent IDs | Verified inbound parents |
|---:|---|---:|---:|---:|
| 1 | `AmazonHelp` | 169,840 | 155,445 | 154,976 |
| 2 | `AppleSupport` | 106,860 | 106,696 | 106,623 |
| 3 | `Uber_Support` | 56,270 | 55,283 | 55,182 |
| 4 | `SpotifyCares` | 43,265 | 41,734 | 41,585 |
| 5 | `Delta` | 42,253 | 36,215 | 36,134 |
| 6 | `Tesco` | 38,573 | 25,315 | 25,282 |
| 7 | `AmericanAir` | 36,764 | 36,524 | 36,457 |
| 8 | `TMobileHelp` | 34,317 | 33,909 | 33,837 |
| 9 | `comcastcares` | 33,031 | 30,455 | 30,369 |
| 10 | `British_Airways` | 29,361 | 24,108 | 24,084 |
| 11 | `SouthwestAir` | 28,977 | 28,346 | 28,285 |
| 12 | `VirginTrains` | 27,817 | 26,373 | 26,272 |
| 13 | `Ask_Spectrum` | 25,860 | 25,165 | 24,976 |
| 14 | `XboxSupport` | 24,557 | 21,305 | 20,213 |
| 15 | `sprintcare` | 22,381 | 20,149 | 20,026 |
| 16 | `hulu_support` | 21,872 | 21,570 | 21,468 |
| 17 | `sainsburys` | 19,466 | 17,735 | 17,717 |
| 18 | `GWRHelp` | 19,364 | 18,562 | 18,506 |
| 19 | `AskPlayStation` | 19,098 | 18,669 | 18,650 |
| 20 | `ChipotleTweets` | 18,749 | 18,578 | 18,565 |

## Candidate brands for the Hiver project

Candidates are the first five accounts above, selected solely from observed outbound-support volume and available reply linkage.
