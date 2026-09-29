# Improve game graphics and visual polish

- STATUS: OPEN
- PRIORITY: 70
- TAGS: graphics, frontend

The TS game renders everything procedurally on canvas (drawNima/drawBackground/drawGround in src/engine/Game.ts, Pillar/Particles) — functional but basic. Audit the current look in npm run dev, then improve in layers: character art (public/images/ holds 40+ legacy sprites currently unused — evaluate integrating them for idle/swing/defeated frames), richer background/particles, and crisper HUD feedback. Keep the WebAudio synth and PROJECT_RULES.md sound policy untouched. Acceptance is a visual review pass, ideally with screenshots attached to the PR.
