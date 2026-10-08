# Seeded bundle spawns with observer capture

- STATUS: OPEN
- PRIORITY: 90
- TAGS: wasm, security, frontend

Close the replay loop on the client: deterministic splitmix64 stream shared by page and sim (seed from launch URL), bundle spawn draws patched to it with round-reset driven by the companion, chop capture via MutationObserver with backfill, PORTING.md for the next language port. Verifies: identical goldens across JS/Rust, green suite, live playtest with save badge.
