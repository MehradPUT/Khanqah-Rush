# Add game-engine test coverage

- STATUS: OPEN
- PRIORITY: 65
- TAGS: tests

tests/ currently holds only a smoke suite guarding repo invariants; src/engine/Game.ts, characters, audio, and telegram/tma.ts have zero coverage. Add focused Vitest unit tests for pure logic first (scoring, pillars, particles), mocking canvas/DOM where needed. Best done after Task(20260929-075552) so tests target the real Vite entry instead of the frozen legacy bundle.
