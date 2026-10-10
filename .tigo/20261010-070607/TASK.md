# Formalize long-term debug system

- STATUS: OPEN
- PRIORITY: 75
- TAGS: docs, server, frontend

Debug tooling is a long-term necessity, but the current surface is ad-hoc TEMP-DEBUG: worker/index.js leaks debugReason on every deny plus crash internals, the per-update log is ungated, and Task(20261008-143305) demands removing all debug instrumentation. Formalize instead: (1) server-side DEBUG_SCORES=1 flag (dev-only: .env for node, .dev.vars for wrangler dev, never production) gating debugReason, crash detail, and worker update logs; production deny responses carry exactly {ok, recorded}. (2) Keep the client ?dbg badge+logs as the permanent dev-mode contract (never client-gated reasons: reject codes would be a cheat oracle). (3) Document in docs/debugging.md, slim docs/companion.md to a link, .env.example entry. (4) Tighten tests: strict no-debugReason assertions by default plus a debug-env case. Acceptance: full suite green, no reason oracle or crash detail reaches players by default, every debug affordance documented. Amends Task(20261008-143305) clause 3.
