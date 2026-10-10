# Companion score reporter (`client/js/score-report.mjs`)

Observes the legacy game from the outside (no bundle surgery except
the seeded RNG, extra keys, and one state getter) and posts WASM-signed
score envelopes on game over. Runs only with launch params (`lt`, `sid`,
`sk`, `seed`); otherwise the game stays local-only.

## What it tracks

- Round bounds via `#page_wrap` classes (`in_game` / `in_result`) plus
  a `MutationObserver` (near-zero delay) with the 500 ms poll as backup.
- Chop inputs via capture-phase key/touch listeners, timestamped
  against round start. Inputs the bundle ignores are excluded through
  `window.khanqahGame` flags (Ali flurry, Parsa sleep, Fargol
  sacrifice cinematic) so both sides agree per input.
- Hero id via `getCharacter()`, frozen into the trace (v2).
- The seeded RNG stream is reset per round by the capture-phase primer
  ahead of the bundle's own handlers.

## Developer visibility

See [debugging.md](debugging.md) — the `?dbg` badge/logs contract.
Players get a silent companion by default.
