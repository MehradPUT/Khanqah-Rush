# Adapt client to Telegram Games platform

- STATUS: OPEN
- PRIORITY: 75
- TAGS: frontend

The game currently loads telegram-web-app.js (Mini App SDK) and shares via openTelegramLink. For the Games platform (see docs/DEPLOYMENT.md): include https://telegram.org/js/games.js, switch the share button to TelegramGameProxy.shareScore() on explicit user gesture, and read launch params via TelegramGameProxy.initParams if needed. Verify against a BotFather-registered game (/newgame): Play opens the Part B URL, share posts to a chat. Keep src/telegram/tma.ts working as fallback outside Telegram.
