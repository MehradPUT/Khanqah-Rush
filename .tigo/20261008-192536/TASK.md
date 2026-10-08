# Migrate build scripts from .mjs to Python with uv

- STATUS: OPEN
- PRIORITY: 65
- TAGS: tooling

Rewrite scripts/check.mjs, scripts/build-wasm.mjs, and scripts/build-frontend.mjs in Python. Use and document uv and uvx by default for running them (setup, pinned versions, no global installs). Add make entries for each script so make is the primary interface. Keep npm run check/wasm:build/frontend:build working (via shims or updated package.json) and update CI workflows, Makefile help, and any AGENTS.md/docs references. Delete the .mjs files at the end. Acceptance: make targets run the Python versions on Windows and Linux; CI green; docs describe the uv-based workflow; no .mjs remains under scripts/.
