# Make the whole codebase readable

- STATUS: OPEN
- PRIORITY: 70
- TAGS: docs

The legacy bundle ships minified and must stay that way: readable game code is for developers only, never for players. Developers read the bundle through docs/bundle-symbols.md (identifier glossary + annotated key functions), which must grow as new bundle regions get mapped. Scope: (1) extend the symbols glossary + annotated reference for any bundle region we touch; (2) readability passes over our own JS (client/server/shared/worker/tests) — small named helpers, no behavior change; (3) remove all debug instrumentation (companion DEBUG/dbg flag, setScore debugReason, setScore crash-catch) before merging to main; (4) keep docs/bundle-map.md and CHANGELOG.md in sync with the code. Acceptance: a developer unfamiliar with the project can trace a full round (input -> bundle -> companion -> server replay -> Telegram write) using only the docs, and no debug affordance reaches players by default. Related: Task(20261007-081530).
