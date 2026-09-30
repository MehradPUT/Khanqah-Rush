# server/

Bot server for the Telegram Games platform.

- [`score-core.js`](score-core.js) — framework-free verification core
  (WebCrypto, no deps; runs on Node and Workers): launch tokens, session
  keys, envelope verification, plausibility checks, `setGameScore`
  descriptor. Unit-tested in `tests/score-core.test.js`.
- [`example.cjs`](example.cjs) — thin `node:http` adapter over the core
  (webhook + answer-with-session flow + `/api/setScore`). Covers game
  launches and scores only; discovery entry points (`/start` game message,
  inline answers) live in `worker/index.js`. Run with env vars (see header). The future Worker entry reuses the same core.
- Full setup: [`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md) Part D.
- Layered design: [`docs/anticheat-future.md`](../docs/anticheat-future.md).
