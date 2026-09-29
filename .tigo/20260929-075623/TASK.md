# Implement WASM-signed score requests with server verification

- STATUS: OPEN
- PRIORITY: 85
- TAGS: security, backend

Blocked by Task(20260929-075601). Re-add score integrity on top of the WASM build (branch feat/signed-score-anticheat): embed a long random build-time-only secret in the WASM binary, HMAC-sign each submission (score + nonce + timestamp) inside WASM, and verify server-side with nonce/timestamp checks, replay rejection, and rate limits. The server must validate Telegram initData and bind scores to the verified user; treat the WASM signature as defense-in-depth, not proof (embedded secrets are extractable). Do NOT reintroduce getter/setter honeypots. Add Vitest coverage for sign/verify without bundle eval hacks. See docs/anticheat-future.md checklist.
