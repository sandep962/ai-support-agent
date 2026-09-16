# Escalation Failure Analysis

Evaluated rows: 250
False positives: 8
False negatives: 39

## Representative False Positives

### APPLE-GOLD-002
- Customer text: @AppleSupport WiFi &amp; calling broken, 50% increase in battery drain, iOS freezes. Seriously? Did y'all bother to do any tests at all?
- Gold escalation: `0`
- Predicted escalation: `1`
- Gold reason: General bug complaint; AI can give standard troubleshooting.
- Model reason: physical repair or service intervention

### APPLE-GOLD-062
- Customer text: Ive had to reset my phone 6 times already today from this new update and my phone freezing😡😡😡 @AppleSupport
- Gold escalation: `0`
- Predicted escalation: `1`
- Gold reason: Routine freezing/software troubleshooting.
- Model reason: Repeated phone freezing issues with new update, suggesting potential hardware or software problem requiring human intervention

### APPLE-GOLD-102
- Customer text: @115858 my icloud fucc’d up. send help.
- Gold escalation: `0`
- Predicted escalation: `1`
- Gold reason: Vague iCloud complaint; standard troubleshooting.
- Model reason: explicit request for human support

### APPLE-GOLD-129
- Customer text: Every time I go to type a long ass message to someone my text app crashes and I lose the whole fucking message I spent typing. @115858 FIX UR SHIT.
- Gold escalation: `0`
- Predicted escalation: `1`
- Gold reason: General app-crash bug report.
- Model reason: transaction investigation

### APPLE-GOLD-134
- Customer text: Ever since iOS update I try to open an app and my 7+ freezes for several minutes. Also my passcode doesn’t appear. @AppleSupport
- Gold escalation: `0`
- Predicted escalation: `1`
- Gold reason: Routine app-freeze troubleshooting.
- Model reason: device freezing and passcode issue after iOS update

## Representative False Negatives

### APPLE-GOLD-037
- Customer text: @219683 @AppleSupport Its Probally IOS 11 Mines Been Hot Mess Since Then,They Still No Fixy,&amp;I Refuse To Pay For A New Iphone (X) Till I Know IOS11 Works,Also When New One Came Out Ironically Now Apple Said On Phone,Mine Might Be Defective,That 2 Since April
- Gold escalation: `1`
- Predicted escalation: `0`
- Gold reason: Apple already flagged possible device defect; needs human follow-up.
- Model reason: routine complaint about product performance and warranty concerns

### APPLE-GOLD-063
- Customer text: @AppleSupport Your verification code SMSs aren't being sent.
- Gold escalation: `1`
- Predicted escalation: `0`
- Gold reason: Account verification issue may require human assistance.
- Model reason: routine troubleshooting question

### APPLE-GOLD-064
- Customer text: @AppleSupport how do you get rid of an Apple ID when you no longer have access to the email account associated with it?
- Gold escalation: `1`
- Predicted escalation: `0`
- Gold reason: Account recovery without email access needs human identity verification.
- Model reason: routine informational question

### APPLE-GOLD-065
- Customer text: @AppleSupport It's the backup on the Mac which my friend is locked out of. It's encrypted. It's asking for password to restore from backup. Isn't that the same as the Apple ID password? All data is stored on Macbook locally.
- Gold escalation: `1`
- Predicted escalation: `0`
- Gold reason: Locked encrypted backup access requires human assistance.
- Model reason: routine troubleshooting question

### APPLE-GOLD-067
- Customer text: @569762 @AppleSupport Hi, I’m having the same issue here. I can’t access anymore to my laptop. I have the login screen then after a blank screen
- Gold escalation: `1`
- Predicted escalation: `0`
- Gold reason: Device access issue requires human troubleshooting.
- Model reason: routine troubleshooting request
