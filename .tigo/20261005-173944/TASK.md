# Phase 3: WASM rebuild with plain-JS loaders

- STATUS: OPEN
- PRIORITY: 80
- TAGS: wasm

Re-add wasm/signer + wasm/sim sources and scripts/build-wasm.mjs (disk copies intact). Port backup src/wasm loaders from TS to plain JS for the legacy page (identical wire protocols: signer v2, sim v1). Re-add WASM Vitest suites unchanged. npm run lint/test/build green.
