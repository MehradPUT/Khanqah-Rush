# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Vim-style `H`/`L` chop keys in the legacy bundle (surgical keydown-patch,
  mirrored to `dist/`; menu carousel keeps arrows).

- WASM rebuild: Rust signer/sim crates with replay CLI, `npm run wasm:build`
  emitting gitignored `public/wasm/` artifacts, and plain-JS page loaders
  (`public/js/*-loader.mjs`) with node:crypto and native-golden cross-checks.

- Repo tooling: Biome (legacy bundle and minified CSS excluded from lint),
  pre-commit hooks, EditorConfig, LF enforcement, Node 24 pin, Vitest
  harness with a legacy-entry smoke test, GitHub Actions CI, Makefile
  shortcuts, `wrangler.toml` (assets-only), and `node scripts/check.mjs`
  syntax checks (`npm run check`).

- Reimplementation on the upstream base (legacy PIXI-bundle game): hygiene,
  tooling, and Gates per `REIMPLEMENTATION.md` (uncommitted plan).
- Games backend: framework-free score verification (`server/score-core.js`,
  launch tokens, session keys, envelope + plausibility checks), reference
  node adapter and production Worker entry (`BOT_USERNAME`/`GAME_SHORT_NAME`
  vars), `npm run deploy`, and bot/webhook Makefile targets.
