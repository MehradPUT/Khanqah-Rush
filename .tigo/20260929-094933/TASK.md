# Remove unused runtime dependencies

- STATUS: CLOSED
- PRIORITY: 55
- TAGS: dx

Neither @twa-dev/sdk nor telegraf is imported anywhere in src/ (src/telegram/tma.ts talks to window.Telegram directly; telegraf was only used by the gitignored scratch/telegram_bot_sample.js). Remove both from package.json dependencies via npm uninstall and verify npm run build plus npm test still pass. If TmaBridge is ever migrated onto the official SDK, re-add @twa-dev/sdk then.
