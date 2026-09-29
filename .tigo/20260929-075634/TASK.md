# Restore curated server/bot example into the repo

- STATUS: OPEN
- PRIORITY: 70
- TAGS: backend

scratch/telegram_bot_sample.js (Express /api/setScore reference) no longer exists on disk — scratch/ was deleted locally and is gitignored. It survives only in git history (e.g. git show 3dae5c8:scratch/telegram_bot_sample.js). Recover it from there and evolve it into the Games-platform server from docs/DEPLOYMENT.md Part D: answer game callback queries with the game URL (answerCallbackQuery), accept score POSTs and call Bot API setGameScore, serve getGameHighScores tables. Keep the env-based token pattern (process.env.TELEGRAM_BOT_TOKEN, never hardcoded; wrangler secret put in production). Same-Worker hosting keeps it free with no KV.
