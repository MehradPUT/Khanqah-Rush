# Implement WASM-signed score requests with server verification

- STATUS: CLOSED
- PRIORITY: 85
- TAGS: security, backend

Implement the layered anti-cheat from docs/anticheat-future.md (branch feat/signed-score-anticheat): 0) bot-only setGameScore writes; 1) webhook secret_token check; 2) HMAC-signed launch tokens bound to user+chat+message; 3) per-session signing keys issued at launch (NOT one global secret baked into WASM — extraction must yield at most one session); 4) signed request envelope (version, ±60s timestamp, 128-bit nonce store, constant-time HMAC, fail closed); 5) plausibility checks + top-score replay verification; 6) silent flag/quarantine with force-demote for confirmed cheaters; 7) anomaly alerting + review queue. Server also answers game callbacks with the URL and exposes /api/setScore. Do NOT reintroduce getter/setter honeypots. Add Vitest coverage for sign/verify without bundle eval hacks.
