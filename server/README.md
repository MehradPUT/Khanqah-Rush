# server/

Reference-only bot server for the Telegram Games platform.

- [`example.cjs`](example.cjs) — dependency-free Node server sketch:
  answers Play callbacks with the game URL and posts scores via
  `setGameScore`. Run with env vars (see header).
- Full setup: [`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md) Part D.
- Real implementation (launch tokens, HMAC envelope, plausibility checks)
  is tracked future work — see `docs/anticheat-future.md`.
