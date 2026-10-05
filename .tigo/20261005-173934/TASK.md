# Phase 2: server and edge port

- STATUS: OPEN
- PRIORITY: 85
- TAGS: backend, telegram

Copy unchanged from backup: server/score-core.js, server/example.cjs, server/README.md, worker/index.js, score-core + worker tests. Proves bundle-independence when green unmodified. Add BOT_USERNAME/GAME_SHORT_NAME vars when known (D5: khanqah_rush). Legacy bundle already calls TelegramGameProxy.shareScore, so no client share work. Verify full suite + wrangler dry-run.
