# Phase 5: deterministic sim alignment and replay

- STATUS: OPEN
- PRIORITY: 85
- TAGS: wasm, security, backend

Extract exact legacy branch-spawn rules from the bundle RE step and align wasm/sim thresholds to them (they currently mirror our old TS Pillar, not the bundle). Regenerate goldens (Rust tests, replay CLI, Vitest cross-checks). Land server replay via sim.wasm plus binary trace packaging, and seed anti-grinding (server-issued seeds in launch tokens, single active seed per user, issuance rate limits, short TTL).
