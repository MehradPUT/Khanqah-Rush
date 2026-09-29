# Confirm removed test bot token was a dummy

- STATUS: OPEN
- PRIORITY: 50
- TAGS: security

The deleted test scripts hardcoded botToken 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 and chatId -100123456789, which look like placeholders, and were replaced with env-based dummy fallbacks before removal. Confirm with the friend/upstream that no real secret was committed; if it was real, rotate the bot token immediately. Close with a comment stating the outcome.
