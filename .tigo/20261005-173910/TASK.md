# Phase 0: hygiene and foundations on upstream base

- STATUS: CLOSED
- PRIORITY: 90
- TAGS: setup

On top of current main (upstream reset): delete stale local leftovers (dist/assets, dist/wasm, public/wasm, keep wasm sources), extend .gitignore (public/wasm, wasm target dirs, .wrangler, coverage), untrack dist/ per D4 (no duplication), npm ci + verify dev/build on the untouched base, re-add AGENTS.md, fresh CHANGELOG, record D1 (PRs to origin/main) and close this task in the completing commit. Branch: chore/rebase-foundations.
