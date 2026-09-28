# Anti-cheat: future plan

## Why the old system was removed

The client-side honeypot (`window.score` getter/setter traps, shadow-score XOR,
`FLAGGED_<reason>` tokens, `untrusted_event` flags in `public/js/main.js`) only
catches players poking values in the dev console. In a Telegram Mini App the
real attack is a forged HTTP request built outside the game, which never touches
those traps — so the system added code and test surface without real protection.
It was removed; the test harness (`tests/anticheat.test.js`,
`test_anticheat_slice.cjs`, `test_honeypot_anticheat.cjs`) went with it.

Note: the frozen legacy bundle `public/js/main.js` still contains the old
honeypot code paths. It is intentionally untouched until the Vite/WASM
migration replaces it (see below) — hand-editing the 496 KB minified bundle
risks breaking the only score-submit path (`qb()`) with no way to verify in
Node (canvas `getContext`).

## Intended replacement: signed score requests

- Embed a long random secret in the WASM binary at build time (never in JS
  source or the repo) and HMAC-sign each score submission
  (`score + nonce + timestamp`) inside WASM.
- Server recomputes the HMAC, rejects bad/expired signatures, enforces
  per-session nonces (replay protection) and sane rate/cps limits.
- Honest caveat: an embedded secret raises the bar but is extractable from any
  shipped binary by a determined attacker. The actual trust anchor must be
  server-side: validate Telegram `initData`, bind scores to the verified user,
  and treat the WASM signature as defense-in-depth, not proof.

## Branch / PR plan (separate from this removal)

1. **Branch `chore/wasm-telegram-prep`** (own PR): WASM build pipeline,
   `index.html` entry migration (`public/js/main.js` → `/src/main.ts`,
   `<canvas id="gameCanvas">` wiring), `dist/` output for Telegram hosting.
   Status: not started — extent of existing WASM/Telegram prep is unknown.
2. **Branch `feat/signed-score-anticheat`** (own PR, on top of the above):
   implement WASM signing + server verification + new tests. Do not reintroduce
   getter/setter honeypots.

## Checklist for the future PR

- [ ] Secret injected at build time only (env/CI secret, long random value).
- [ ] Server validates Telegram `initData` and binds score to verified user.
- [ ] Nonce + timestamp verification, replay rejection, rate limits.
- [ ] New Vitest coverage for sign/verify (no bundle `eval` hacks).
- [ ] This doc and the README updated to point at the new design.
