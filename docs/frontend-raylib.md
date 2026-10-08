# Raylib + Rust frontend (`frontend/`)

Reimplementation of the game frontend in Rust with Raylib, compiled to
WebAssembly via Emscripten. Replaces the legacy PIXI bundle for
consistent rendering across devices — notably the invisible branches
and stamina bar on some mobile GPUs, which an explicit redraw loop
fixes by construction.

Status: Phase 1 spike (window + text through the full toolchain).
The legacy frontend stays the default entry until the rewrite is
verified; it remains playable behind a flag afterwards.

## Toolchain

- Rust (MSRV 1.88; repo pins Node 24, Rust follows upstream) +
  `wasm32-unknown-emscripten` target.
- Emscripten SDK (`EMSDK` env var, or `emcc` on PATH — never
  hardcoded); CMake; Ninja or MinGW Makefiles on Windows.
- `raylib` crate 6.0 from crates.io (vendored C build via raylib-sys).

Build: `npm run frontend:build` (debug) or
`node scripts/build-frontend.mjs --release`. Tolerant: without the
toolchain it warns and skips. Artifacts land in `public/game/`
(gitignored, served as static assets).

Windows lessons (em regimen; see `scripts/build-frontend.mjs`):
`EMCC_CFLAGS` is mandatory; `CC`/`CXX`/`AR` must point at the `.exe`
launchers (the crate guesses `emar.bat`, which no longer ships);
bindgen needs the emscripten sysroot with forward slashes; rustc's
linker must be overridden to `emcc.exe`; emcmake defaults to MinGW
Makefiles (Ninja is rejected by the toolchain file on Windows).

## Architecture (target)

- `frontend/src/`: `main.rs` (entry/loop), later `scene/` (tree,
  lumberjack, effects), `hud/` (bars, carousel, result), `audio/`,
  `sim_bridge/` (Rust port of `shared/sim.js` mechanics for
  frame-accurate local play; server replay stays authoritative).
- Assets load from the same `public/` tree (PNG sprites, MP3, TTF)
  embedded via Emscripten `--preload-file` (Phase 2).
- Page wiring (Phase 2): new entry (e.g. `game.html`) loading
  `public/game/khanqah-frontend.js`; launch params and the companion
  reporter attach unchanged (trace v2 + envelopes are renderer-blind).
- Tests: `software_renderer` headless pixel probes for rendering
  regressions; sim parity against `shared/sim.js` goldens; phone +
  desktop playtests before the flag flip.

## Phase plan

1. Spike: compile + link through the whole chain. (Done.)
2. Page + boot: shell template (`frontend/shell.html`), build emits
   `public/game/index.html` + loader + WASM, `/game/` serves all
   three with correct types. (Done, verified locally.)
3. Scene port (tree, lumberjack, chop effects) to visual parity.
4. Assets (`--preload-file`), HUD, carousel, result screen, audio,
   haptics hooks.
5. Sim bridge + input parity; pixel + outcome regression tests.
6. Flag flip with legacy fallback; playtest matrix.
