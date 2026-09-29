# Implement production Worker server entry

- STATUS: CLOSED
- PRIORITY: 85
- TAGS: backend, telegram

The deployed Worker serves static assets only, so Telegram callbacks go nowhere. Add worker/index.js: fetch handler routing POST /telegram-webhook (secret check, answerCallbackQuery with session-minted URL) and POST /api/setScore (launch token, envelope, plausibility, setGameScore) over server/score-core.js, falling through to env.ASSETS for static files. Secrets via wrangler secret put (TELEGRAM_BOT_TOKEN, SERVER_SECRET, WEBHOOK_SECRET); GAME_SHORT_NAME in wrangler vars. Update DEPLOYMENT Part D, wrangler.toml, README/CHANGELOG. Does not include multilevel monitoring (layer 7).
