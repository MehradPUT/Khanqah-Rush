# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `.gitignore` covering dependencies, build output, `scratch/`, `tmp/`,
  editor artefacts, secrets (`.env`), and Python/test caches.
- `README.md` with setup, project layout, sound policy, and fork workflow.
- `AGENTS.md` with verification workflow, Tigo task tracking, and conventions.
- Vitest suite (`tests/smoke.test.js`) guarding repo invariants via `npm test`.
- Biome lint/format (`npm run lint`, `npm run format`) with
  `.pre-commit-config.yaml` hooks and `.editorconfig`.
- `.env.example` with dummy Telegram/bot placeholders.
- `docs/anticheat-future.md` with the planned WASM-signed score design.
- `npm run check` (`tsc --noEmit`) typecheck script.

### Changed

- Test bot tokens/chats now come from env (`TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_CHAT_ID`) with dummy offline fallbacks instead of hardcoded values.

### Removed

- Client honeypot anti-cheat harness and its tests
  (`tests/anticheat.test.js`, `test_anticheat_slice.cjs`,
  `test_honeypot_anticheat.cjs`); it could not stop forged requests.
  The frozen legacy bundle still contains the old code paths until the
  Vite/WASM migration replaces it.

### Security

- Untracked `node_modules/`, `dist/`, and `scratch/` from git (kept on disk,
  now ignored) so build artefacts and local tooling no longer ship in history.
- Removed hardcoded test bot token/chat id from tracked test scripts.
