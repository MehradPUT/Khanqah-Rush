# Anti-cheat: future plan

## Why the old system was removed

The client-side honeypot (`window.score` getter/setter traps, shadow-score XOR,
`FLAGGED_<reason>` tokens, `untrusted_event` flags in `public/js/main.js`) only
catches players poking values in the dev console. In a Telegram Mini App the
real attack is a forged HTTP request built outside the game, which never touches
those traps — so the system added code and test surface without real protection.
It was removed; the test harness (`tests/anticheat.test.js`,
`test_anticheat_slice.cjs`, `test_honeypot_anticheat.cjs`) went with it.

Note: the legacy bundle `public/js/main.js` (which still contained the old
honeypot code paths) was deleted together with the Vite entry migration
(`feat/vite-entry-migration`) instead of being hand-edited — the 496 KB
minified bundle could not be safely stripped by hand, and its only
score-submit path (`qb()`) had no Node-verifiable cover (canvas `getContext`).

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

1. **Branch `chore/wasm-telegram-prep`** (own PR): WASM toolchain scaffold
   (Rust stub + TS loader, `npm run wasm:build`), `index.html` entry migration
   (`public/js/main.js` → `/src/main.ts`, `<canvas id="gameCanvas">` wiring),
   and Cloudflare Workers static hosting for `dist/`. Done — remaining prep
   is the BotFather/Mini App wiring in `docs/telegram-hosting.md`.
2. **Branch `feat/signed-score-anticheat`** (own PR, next): replace the stub
   with real HMAC-SHA256 signing (build-time secret) + server verification +
   new tests. Do not reintroduce getter/setter honeypots.
2. **Branch `feat/signed-score-anticheat`** (own PR, on top of the above):
   implement WASM signing + server verification + new tests. Do not reintroduce
   getter/setter honeypots.

## Checklist for the future PR

- [ ] Secret injected at build time only (env/CI secret, long random value).
- [ ] Server validates Telegram `initData` and binds score to verified user.
- [ ] Nonce + timestamp verification, replay rejection, rate limits.
- [ ] New Vitest coverage for sign/verify (no bundle `eval` hacks).
- [ ] This doc and the README updated to point at the new design.
