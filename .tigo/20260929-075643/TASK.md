# Add CI workflow (install, build, test, lint)

- STATUS: OPEN
- PRIORITY: 75
- TAGS: ci

There is no .github/workflows/ci.yml. Add one running on push/PR: npm ci, npm run check (tsc --noEmit), npm test (vitest run), npm run lint (biome check), npm run build. Use dummy env values (see .env.example) so the pipeline runs offline. Unblocks the PR in Task(20260929-075544) from relying on manual verification.
