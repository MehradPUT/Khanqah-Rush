# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Reference Games bot server (`server/example.cjs`, dependency-free):
  answers Play callbacks with the game URL and posts scores via
  `setGameScore`; recovered from history after `scratch/` left the disk.

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
- Rust WASM signer stub (`wasm/signer`, 473-byte `signer.wasm`): TS loader
  with graceful degradation, `npm run wasm:build` (tolerant without Rust),
  `prebuild` hook, and loader tests.
- Cloudflare Workers static hosting for `dist/` (`wrangler.toml`,
  `npm run deploy`, `docs/telegram-hosting.md`); no KV/storage, free tier.
- `.gitattributes` enforcing LF line endings so Biome stays green on checkout.
- `docs/DEPLOYMENT.md`: complete walkthrough from `npm run build` to BotFather
  Mini App registration (`/newapp` short name), Workers deploy, and the
  in-Telegram verification checklist.
- `docs/DEPLOYMENT.md` rewritten for the Telegram Games platform (`/newgame`
  short name as Game ID, per-launch URL via `answerCallbackQuery`,
  `setGameScore` server contract); removed the superseded Mini-App-oriented
  `docs/telegram-hosting.md`.
- `docs/anticheat-future.md` rewritten as a layered defense design (platform
  guarantees, webhook auth, launch-bound sessions, per-session signing keys,
  signed envelopes, plausibility checks, silent enforcement, monitoring)
  from current anti-cheat research.
- GitHub Actions CI (`.github/workflows/ci.yml`) running check, test, lint,
  and build on push/PR, pinned to Node 24 via `.nvmrc`.
- Vite shell `index.html` for the TS game (all DOM hooks, `/src/main.ts`
  entry, `game.css` import); `npm run build` emits a 25KB bundle.

### Changed

- UI and Persian fonts switched to Vazirmatn (with Latin fallbacks),
  replacing Cinzel/Amiri/Outfit.

- Applied Biome formatting and safe lint fixes repo-wide (`import type`,
  `**` operator, removed unused `BranchSide` import and empty constructor);
  `npm run lint` now passes on the whole repo.
- Test bot tokens/chats now come from env (`TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_CHAT_ID`) with dummy offline fallbacks instead of hardcoded values.

### Removed

- Unused runtime dependencies (`@twa-dev/sdk`, `telegraf`); nothing in
  `src/` imported them.

- Client honeypot anti-cheat harness and its tests
  (`tests/anticheat.test.js`, `test_anticheat_slice.cjs`,
  `test_honeypot_anticheat.cjs`); it could not stop forged requests.
- Legacy web bundle (`public/js/main.js`, `public/css/main.min.css`) and the
  legacy shell UI (character carousel, leaderboard table), superseded by the
  Vite TS entry. Carousel/leaderboard have no TS counterpart yet.

### Security

- Untracked `node_modules/`, `dist/`, and `scratch/` from git (kept on disk,
  now ignored) so build artefacts and local tooling no longer ship in history.
- Removed hardcoded test bot token/chat id from tracked test scripts.
