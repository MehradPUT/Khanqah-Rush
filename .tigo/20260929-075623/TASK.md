# Implement WASM-signed score requests with server verification

- STATUS: OPEN
- PRIORITY: 85
- TAGS: security, backend

Implement WASM-signed score requests with server verification (branch feat/signed-score-anticheat). The server leg is now defined by the Games platform (see docs/DEPLOYMENT.md Part D): the game POSTs to your own server, which validates and calls Bot API setGameScore (Telegram stores the board and announces records; use force only to demote cheaters; getGameHighScores for tables). Client leg: embed a long random build-time-only secret in the WASM binary and HMAC-sign each submission (score + nonce + timestamp) inside WASM; server verifies with nonce/timestamp checks, replay rejection, and rate limits. The server must also answer game callback queries with the game URL (answerCallbackQuery). Do NOT reintroduce getter/setter honeypots. Add Vitest coverage for sign/verify without bundle eval hacks.
