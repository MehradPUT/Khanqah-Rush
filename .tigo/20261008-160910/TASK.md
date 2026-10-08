# Rewrite game frontend with Raylib and Rust targeting WASM

- STATUS: OPEN
- PRIORITY: 85
- TAGS: frontend, wasm

Reimplement the game frontend (rendering, input, HUD) in Rust with Raylib, compiled to WebAssembly, replacing the legacy PIXI bundle for better performance and consistent behavior across devices. The new UI must look exactly the same as the current one: same layout, sprites, character carousel, HUD, ability bars, result screen, and game feel. Must fix the current rendering bug where branches and the stamina bar go invisible on some devices (especially mobile). Hard constraints: keep the verified contracts intact — seeded RNG spawn stream, chop/death/stamina mechanics per docs/bundle-map.md, trace v2 + signed envelope flow, launch params, Telegram Games integration, and server replay verification (shared/sim.js parity). Acceptance: pixel-identical UI side-by-side with the current build; branches and stamina bar visible on the affected mobile devices; same gameplay timing and mechanics (sim parity holds); full test suite green plus rendering regression coverage; playtested on phone and desktop before replacing the legacy frontend. Keep the legacy bundle playable behind a flag until the rewrite is verified.
