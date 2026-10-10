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
  rngDraws, lastPoll}`) is exposed in **both** modes — it carries no
  secrets. `rngDraws` is the seeded-stream draw count below.

## Seeded-RNG draw telemetry (dev-only, client-side)

The seeded spawn stream (`public/js/seeded-rng.js`) exposes
`window.__rngDraws`: seeded `window.__rng50()` draws consumed since
page load or the last `window.__rngReset()`. The companion primer
resets the stream at every round start, so the count is per-round.
Unseeded opens fall back to `Math.random()` and never increment it.
Production behavior is unchanged — the counter is observability only.

- `window.__khanqah.rngDraws` (always-on object, refreshed each poll)
  and `window.__khanqah.lastPoll.rngDraws` carry the current count.
- `?dbg` logs (`round start seen`, `round frozen for report`,
  `game over seen`, `firing report`) include `rngDraws`, so a replay
  `no-outcome-match` (surfaced on the wire as
  `replay-no-outcome-match`) can be checked against stream position:
  5 draws after reset is round init, then one draw per odd-length chop
  replenish (see `docs/bundle-map.md`).
- The trace wire format (v2) is unchanged. Sending the count to the
  server for first-divergence reporting is a follow-up: it must land
  as an additive, version-tolerant extension with tests.

## Seeded-stream primer (determinism check)

With `?dbg`, the companion logs `round start seen` with the `#page_wrap`
classes at each round transition. To confirm the seeded spawn stream was
not reset mid-round: start a seeded round, chop through an input-ignoring
window (Fargol sacrifice, Parsa nap, Ali flurry), and check the server
verdict -- a mid-round reset would diverge replay and reject the score.
The ordering proof (bundle bubble vs companion capture, single `in_game`
toggle site, idempotent `__rngReset`) is recorded in `docs/bundle-map.md`.

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
