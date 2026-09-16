# Ollama AI Classifier Failure Analysis

Model: `llama3.2`
Evaluation rows: `250`
Incorrect predictions: `119`
Correct predictions: `131`

## Overall Comparison

| System | Accuracy | Macro F1 |
|---|---:|---:|
| Majority | 0.248 | 0.0441595 |
| TF-IDF + Logistic Regression | 0.624 | 0.5647142 |
| Ollama `llama3.2` | 0.524 | 0.5159378 |

Ollama is substantially above the Majority baseline, but below the TF-IDF + Logistic Regression baseline on both accuracy and macro F1.

## Confusion Matrix

Rows are gold labels; columns are predicted labels.

| Gold \\ Predicted | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | OTHER_OR_AMBIGUOUS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 9 | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 13 |
| 2 | 1 | 38 | 0 | 7 | 5 | 3 | 0 | 0 | 8 |
| 3 | 0 | 2 | 10 | 9 | 0 | 0 | 1 | 0 | 2 |
| 4 | 0 | 0 | 0 | 16 | 6 | 0 | 0 | 0 | 1 |
| 5 | 0 | 4 | 0 | 2 | 26 | 1 | 1 | 0 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 |
| 7 | 0 | 3 | 0 | 7 | 1 | 2 | 6 | 0 | 11 |
| 8 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 7 | 2 |
| OTHER_OR_AMBIGUOUS | 1 | 2 | 0 | 2 | 0 | 2 | 0 | 0 | 10 |

## Per-Class Metrics

| Label | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.8182 | 0.3462 | 0.4865 | 26 |
| 2 | 0.7308 | 0.6129 | 0.6667 | 62 |
| 3 | 1.0000 | 0.4167 | 0.5882 | 24 |
| 4 | 0.2909 | 0.6957 | 0.4103 | 23 |
| 5 | 0.6842 | 0.6667 | 0.6753 | 39 |
| 6 | 0.5294 | 1.0000 | 0.6923 | 9 |
| 7 | 0.7500 | 0.2000 | 0.3158 | 30 |
| 8 | 1.0000 | 0.3500 | 0.5185 | 20 |
| OTHER_OR_AMBIGUOUS | 0.1923 | 0.5882 | 0.2899 | 17 |

Macro averages: precision `0.6662`, recall `0.5418`, F1 `0.5159`.

## Errors By Gold Intent

| Gold label | Incorrect predictions |
|---|---:|
| 1 | 17 |
| 2 | 24 |
| 3 | 14 |
| 4 | 7 |
| 5 | 13 |
| 6 | 0 |
| 7 | 24 |
| 8 | 13 |
| OTHER_OR_AMBIGUOUS | 7 |

## Errors By Predicted Intent

This counts only incorrect predictions.

| Predicted label | Incorrect predictions |
|---|---:|
| 1 | 2 |
| 2 | 14 |
| 3 | 0 |
| 4 | 39 |
| 5 | 12 |
| 6 | 8 |
| 7 | 2 |
| 8 | 0 |
| OTHER_OR_AMBIGUOUS | 42 |

## Top Five Confusion Pairs

| Gold -> Predicted | Count |
|---|---:|
| 1 -> OTHER_OR_AMBIGUOUS | 13 |
| 7 -> OTHER_OR_AMBIGUOUS | 11 |
| 8 -> 4 | 11 |
| 3 -> 4 | 9 |
| 2 -> OTHER_OR_AMBIGUOUS | 8 |

## High-Confidence Errors

- `high_confidence_wrong_0.8`: **103** errors with confidence >= 0.8.
- `high_confidence_wrong_0.9`: **22** errors with confidence >= 0.9.

The representative examples below include several high-confidence errors. The recorded reasons are reproduced from the prediction file; no additional explanation is inferred.

## Representative Incorrect Predictions

1. **APPLE-GOLD-004**
   Customer text: `@342218 @115858 Amen. Any fix for the battery drain?`
   Gold: `1` | Predicted: `OTHER_OR_AMBIGUOUS` | Confidence: `0.800000`
   Reason: `unclear/insufficient information`

2. **APPLE-GOLD-002**
   Customer text: `@AppleSupport WiFi &amp; calling broken, 50% increase in battery drain, iOS freezes. Seriously? Did y'all bother to do any tests at all?`
   Gold: `7` | Predicted: `OTHER_OR_AMBIGUOUS` | Confidence: `0.800000`
   Reason: `unclear/insufficient information`

3. **APPLE-GOLD-023**
   Customer text: `It is very difficult to get Genuine Iphone Charger or Headphone, I need original IPhone charger please suggest  @AppleSupport`
   Gold: `8` | Predicted: `4` | Confidence: `0.800000`
   Reason: `iCloud, backup, restore, and data sync`

4. **APPLE-GOLD-068**
   Customer text: `@AppleSupport you goons aren't letting me contact support because my phone is dead and you keep sending it codes. What the butt? How is that smart? Two-Factor Authentication DOES NOT WORK when a device isn't operational.`
   Gold: `3` | Predicted: `4` | Confidence: `0.900000`
   Reason: `iCloud, backup, restore, and data sync`

5. **APPLE-GOLD-012**
   Customer text: `@AppleSupport So I’ve had a look at https://t.co/ACdWGNywii, it’s not showing all my photos. My iPhone it but it seems to have broken albums down between iPhone photos and ones I’ve added from my camera.`
   Gold: `4` | Predicted: `5` | Confidence: `0.800000`
   Reason: `Apps / App Store / media downloads`

6. **APPLE-GOLD-008**
   Customer text: `@AppleSupport how about you fix the battery with the iOS 11 I have an iPhone SE and ever since I did the upgrade it’s horrible.`
   Gold: `2` | Predicted: `OTHER_OR_AMBIGUOUS` | Confidence: `0.400000`
   Reason: `unclear/insufficient information`

7. **APPLE-GOLD-015**
   Customer text: `@AppleSupport Thanks for making it damn near impossible to move and/or delete apps off the home screen. Also your automatic WiFi turn on is bullshit. Getting to the point where I hate apple. Last iPhone I ever buy.`
   Gold: `5` | Predicted: `OTHER_OR_AMBIGUOUS` | Confidence: `0.800000`
   Reason: `complaints about Apple's design choices and features, without a clear technical issue to report`

8. **APPLE-GOLD-169**
   Customer text: `@AppleSupport I bought a @181575 iPhone X case 3 weeks ago and it blocks the microphone. It happens on every call I make or receive and people complain that they can’t hear me. Can I get a refund?`
   Gold: `7` | Predicted: `4` | Confidence: `0.900000`
   Reason: `iCloud, backup, restore, and data sync`

9. **APPLE-GOLD-007**
   Customer text: `@AppleSupport why my iPhone battery dying so fast ????`
   Gold: `1` | Predicted: `2` | Confidence: `0.800000`
   Reason: `iOS and software behavior / updates`

10. **APPLE-GOLD-009**
    Customer text: `Hey @AppleSupport I literally watched as my battery on my iPhone6 dropped 60% to 40% because I bought and downloaded and album. I hope 11.2 fixes this.`
    Gold: `2` | Predicted: `5` | Confidence: `0.800000`
    Reason: `Apps / App Store / media downloads`

11. **APPLE-GOLD-096**
    Customer text: `Smh @115858 can’t even restore my new phone 🙄🙄🙄`
    Gold: `4` | Predicted: `OTHER_OR_AMBIGUOUS` | Confidence: `0.800000`
    Reason: `unclear/insufficient information`

12. **APPLE-GOLD-225**
    Customer text: `@AppleSupport i have a question about iPhone x pre order and Att next`
    Gold: `8` | Predicted: `OTHER_OR_AMBIGUOUS` | Confidence: `0.500000`
    Reason: `unclear/insufficient information`

13. **APPLE-GOLD-058**
    Customer text: `@AppleSupport 6s. iOS 11.1 beta 5`
    Gold: `OTHER_OR_AMBIGUOUS` | Predicted: `6` | Confidence: `0.800000`
    Reason: `Billing, payments, subscriptions, refunds`

14. **APPLE-GOLD-061**
    Customer text: `@115858 why is my iMessage not working bro`
    Gold: `5` | Predicted: `2` | Confidence: `0.900000`
    Reason: `iOS and software behavior / updates`

15. **APPLE-GOLD-075**
    Customer text: `@AppleSupport The iPad's password`
    Gold: `3` | Predicted: `2` | Confidence: `0.800000`
    Reason: `iOS and software behavior / updates`

16. **APPLE-GOLD-168**
    Customer text: `Hey @115858 after my phone auto updated iOS it has dropped EVERY SINGLE CALL. Fix r send me a refund for a phone that now doesn’t work.`
    Gold: `7` | Predicted: `6` | Confidence: `0.900000`
    Reason: `Billing, payments, subscriptions, refunds`

17. **APPLE-GOLD-037**
    Customer text: `@219683 @AppleSupport Its Probally IOS 11 Mines Been Hot Mess Since Then,They Still No Fixy,&amp;I Refuse To Pay For A New Iphone (X) Till I Know IOS11 Works,Also When New One Came Out Ironically Now Apple Said On Phone,Mine Might Be Defective,That 2 Since April`
    Gold: `2` | Predicted: `4` | Confidence: `0.800000`
    Reason: `iCloud, backup, restore, and data sync`

## Observed Patterns From These Examples

These are descriptions of the recorded examples, not classifier changes or causal claims:

- Several errors assign `OTHER_OR_AMBIGUOUS` to messages that contain an explicit issue, including battery drain, Wi-Fi/calling failure, iOS-related battery behavior, and restore failure.
- Several errors assign `4` to messages whose text explicitly mentions two-factor authentication, calls, a charger, or an iOS problem.
- Battery-related wording appears with multiple gold labels in the representative set: `1` for direct battery drain, `2` when tied to an iOS update, and `5` when tied to a downloaded album.
- Some messages contain multiple issue cues, such as Wi-Fi plus app movement, calls plus refund language, or calls plus a case blocking a microphone.
- The model produced high confidence on multiple incorrect predictions, including examples `APPLE-GOLD-068`, `APPLE-GOLD-169`, `APPLE-GOLD-061`, and `APPLE-GOLD-168`.

No classifier, taxonomy, golden-set, baseline, or evaluation files were modified for this analysis.
