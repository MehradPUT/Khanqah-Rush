# Restore curated server/bot example into the repo

- STATUS: OPEN
- PRIORITY: 70
- TAGS: backend

scratch/telegram_bot_sample.js (Express /api/setScore reference with Telegram alert logic) no longer exists on disk — scratch/ was deleted locally and is gitignored. It survives only in git history (e.g. git show 3dae5c8:scratch/telegram_bot_sample.js). Recover it from there, curate it into the repo (e.g. server/example.js or docs/), keep the env-based token pattern (process.env.TELEGRAM_BOT_TOKEN, never hardcoded), and document that it is a reference only. Needed as a starting point for real server-side score verification.
