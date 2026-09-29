# Anti-cheat: future plan

## Why the old system was removed

The client-side honeypot (`window.score` getter/setter traps, shadow-score XOR,
`FLAGGED_<reason>` tokens, `untrusted_event` flags in `public/js/main.js`) only
catches players poking values in the dev console. In a Telegram Game the
real attack is a forged HTTP request built outside the game, which never touches
those traps — so the system added code and test surface without real protection.
It was removed; the test harness (`tests/anticheat.test.js`,
`test_anticheat_slice.cjs`, `test_honeypot_anticheat.cjs`) went with it.

Note: the legacy bundle `public/js/main.js` (which still contained the old
honeypot code paths) was deleted together with the Vite entry migration
(`feat/vite-entry-migration`) instead of being hand-edited — the 496 KB
minified bundle could not be safely stripped by hand, and its only
score-submit path (`qb()`) had no Node-verifiable cover (canvas `getContext`).

## Threat model

Proven attacks against Lumberjack-style Telegram games are console-paste
scripts that set a `DESIRED_SCORE` through the game's own submit path, plus
forged/replayed HTTP requests built outside the game entirely. Design for
those two first; accept that perfect autoplay bots (software playing
legitimately) can only ever be detected statistically, never prevented.

## Layered defense (combine all of these)

No single measure survives contact with a debugger — the research consensus
and industry practice (server-authoritative scoring, signed envelopes,
silent enforcement) is to stack independent layers so each kills a class
of attack:

0. **Telegram platform freebies.** Scores can only be written by the bot
   (`setGameScore`); Telegram rejects score decreases by default, announces
   new records with service messages, and keeps the scoreboard. Never put
   the bot token in the client — score writes go through your server.
1. **Authenticated webhook.** Set BotFather's webhook with a `secret_token`
   and reject any update missing the
   `X-Telegram-Bot-Api-Secret-Token` header. This authenticates the
   Telegram→server direction (callback queries carry the trusted
   user/chat/message ids).
2. **Launch-bound sessions.** When answering the Play callback query, embed
   a server-signed launch token in the game URL (HMAC of
   user + chat + message + expiry with the server secret, same
   sort-and-hash pattern as Telegram's own `initData` validation). The
   server only accepts score posts presenting a live token — this kills
   offline-fabricated submissions, which have no token.
3. **Per-session signing keys, not one global secret.** At launch, the
   server derives a short-lived session key (HMAC of server secret +
   launch token) and hands it to the client over TLS; WASM keeps it in
   memory and HMAC-signs each score post with it. A extracted binary yields
   no long-term secret — at worst one session's key. This supersedes the
   original "long secret baked into WASM" idea, which falls to string
   extraction (same key for all clients, documented weakness).
4. **Signed request envelope.** Every score post carries version +
   timestamp (±60s window) + 128-bit nonce (stored ≥180s, duplicates
   rejected) + HMAC-SHA256 over the canonical payload (method, path,
   timestamp, nonce, body hash). Verify with constant-time comparison and
   fail closed. Kills tampering and replay.
5. **Plausibility validation.** The server independently checks the score
   against game physics: max credible chops/sec, score-vs-duration curve,
   monotonic per-session sequence numbers. Verify top-percentile scores by
   replaying the submitted input/telemetry trace server-side instead of
   trusting the total.
6. **Silent enforcement.** Accept-and-flag rather than instant visible
   rejection — never reveal which check fired. Quarantine suspect scores
   off the public board, and demote/remove confirmed cheaters with
   `setGameScore(force=true)` (score `0` deletes the entry). Keep
   `edit_message` updates for legitimate boards only.
7. **Monitoring.** Alert on anomaly spikes (impossible velocities, score
   floods from one chat), keep a review queue, and rotate server secrets on
   leak suspicion. Statistical detection is triage, not proof — expect and
   budget for false positives.

## Branch / PR plan

1. **Branch `chore/wasm-telegram-prep`** (own PR): WASM toolchain scaffold
   (Rust stub + TS loader, `npm run wasm:build`), `index.html` entry migration
   (`public/js/main.js` → `/src/main.ts`, `<canvas id="gameCanvas">` wiring),
   Cloudflare Workers static hosting for `dist/`, and `docs/DEPLOYMENT.md`.
   Done.
2. **Branch `feat/signed-score-anticheat`** (own PR, next): the bot server
   (callback answers, `/api/setScore` → `setGameScore`), the layered design
   above, and new tests. Do not reintroduce getter/setter honeypots.

## Checklist for the future PR

- [ ] Webhook `secret_token` verified on every update.
- [ ] Launch tokens: HMAC-signed, expiry-checked, bound to user+chat+message.
- [ ] Per-session signing keys issued at launch; no long-term secret in the binary.
- [ ] Envelope verified: version, timestamp window, nonce uniqueness, constant-time HMAC.
- [ ] Plausibility checks (rate/duration/sequence) + top-score replay verification.
- [ ] Silent flag/quarantine path; `force`-demote flow for confirmed cheaters.
- [ ] Anomaly alerting + review queue documented.
- [ ] New Vitest coverage for sign/verify (no bundle `eval` hacks).
- [ ] This doc and the README updated to point at the new design.
