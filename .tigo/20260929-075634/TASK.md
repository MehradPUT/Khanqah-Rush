# Restore curated server/bot example into the repo

- STATUS: OPEN
- PRIORITY: 70
- TAGS: backend

scratch/telegram_bot_sample.js (Express /api/setScore reference with Telegram alert logic) currently lives only in the gitignored scratch/ directory, so collaborators cannot see it. Curate it back into the repo (e.g. server/example.js or docs/), keep the env-based token pattern (process.env.TELEGRAM_BOT_TOKEN, never hardcoded), and document that it is a reference only. Needed as a starting point for real server-side score verification.
