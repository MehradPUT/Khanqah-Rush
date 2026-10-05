# Phase 1: repo tooling from backup

- STATUS: CLOSED
- PRIORITY: 85
- TAGS: setup, dx

Port tooling from backup branch: Biome (.gitignore dist + bundle from lint), pre-commit, editorconfig, .gitattributes LF, .nvmrc, .env.example (server env), CI workflow adapted (node --check or allowJs checkJs since no TS), Makefile (keep verify/deploy/bot targets), vitest config + harness, wrangler.toml assets-only to start, .gitignore additions. Verify lint/test/build green.
