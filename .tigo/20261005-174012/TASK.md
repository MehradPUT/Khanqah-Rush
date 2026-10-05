# Phase 4: legacy-bundle integration (RE, H/L keys, signed reporting)

- STATUS: OPEN
- PRIORITY: 90
- TAGS: frontend, security

Only phase touching the 494KB bundle: surgical string edits only, log before/after SHA-256 in commits, mirror public/ and dist/ identically. Steps: RE the score submitter, branch RNG, and keyboard handler (document offsets); add H/L keyCodes 72/76 (no synthetic-event shim — bundle flags isTrusted===false); signed reporting via companion script observing game-over preferred over bundle surgery; honeypot stays live per D3; regression tests for DOM ids + keycode literals + envelope shape.
