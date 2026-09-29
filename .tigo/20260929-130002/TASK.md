# Deterministic simulation core with replay verification

- STATUS: OPEN
- PRIORITY: 90
- TAGS: wasm, security, backend

Port the authoritative game simulation (branches, score, stamina, phases, death) to integer-only Rust in wasm/sim, used by the TS game via WASM and by the server for replay verification (same artifact both sides, incl. Workers). Includes: seeded PRNG (no Math.random in scored paths), fixed-timestep ms timers, binary+compressed trace packaging client-side, server replay check in score-core, seed anti-grinding (single active seed per user, rate-limited issuance, short TTL), and multi-commit delivery on feat/deterministic-sim. Follow-up of Task(20260929-075623).
