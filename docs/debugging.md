# Debugging contract

Two independent dev-modes, one rule: **players never receive debug
output by default**. Every affordance below is documented here; nothing
else in the codebase emits diagnostics to clients.

## Client dev-mode (`?dbg`)

`client/js/score-report.mjs` reads `URLSearchParams.has("dbg")` — any
value (including bare `?dbg`) enables it.

- Save badge (`#khanqah-save-badge`): `● REC` while recording, then
  `✓ score saved` or `✗ <reason>`. Without a server reason it falls
  back to `✗ not recorded`.
- `[khanqah-debug]` console logs for round transitions, freeze, sign,
  and POST verdicts. Never logs secrets (key/token/tag/trace).
- `window.__khanqah` (`{hasLaunch, recording, lastReport, chops,
  lastPoll}`) is exposed in **both** modes — it carries no secrets.

## Server dev-mode (`DEBUG_SCORES=1`)

`server/score-core.js` exports `isDebugEnabled(env)` (strict `"1"`
match), honored by both transports. Dev-only: `.env` for
`node server/example.cjs`, `.dev.vars` for `wrangler dev`. **Never set
it in production.**

| Behavior | Production (flag off) | Dev (flag on) |
|---|---|---|
| Deny body | exactly `{ok: true, recorded: false}` | adds `debugReason` |
| Crash body | exactly `{ok: true, recorded: false}` | adds `debugReason: "crash:…"` |
| Worker per-update log | silent | `[worker] update: …` |
| Rejection `console.warn` | on (server-side only) | on (server-side only) |

## Why reasons are server-gated, never client-gated

Reject codes (`bad-launch`, `replay-…`, `plausibility-…`) describe the
verifier's decision boundary. A client-controlled switch would turn
them into a cheat oracle for grinding valid-looking scores, so the
server decides alone. The client only renders a reason the server
volunteered.
