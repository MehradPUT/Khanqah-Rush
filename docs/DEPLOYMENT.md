# Deployment (Telegram Game)

End-to-end guide: configure the code, host it on Cloudflare Workers (free,
no storage), register the bot and Game with BotFather, run the score server,
and verify. Follow top to bottom; each part ends with a checkpoint.

## What is being deployed

This project ships as a Telegram **Game** (Bot API Games platform), not a
Mini App:

- **Game page** (`dist/`, built by `npm run build`): static HTML5 game served
  over HTTPS by Cloudflare Workers. Played inside Telegram's in-app browser.
- **Game registration**: BotFather `/newgame` yields a **short name** — the
  Game ID. The bot sends the game with `sendGame(game_short_name)`; the Play
  button raises a callback query that **your server answers with the game URL**
  (`answerCallbackQuery(url=...)`), optionally per-user (the hook where
  signed launch params will go — see `docs/anticheat-future.md`).
- **Scores via Telegram.** The game page POSTs results to your own server
  (the bot token must never reach the browser); the server calls
  `setGameScore`, and **Telegram itself stores the leaderboard, updates the
  scoreboard, and announces new records with service messages**. Fetch tables
  with `getGameHighScores`. Cheaters can be demoted with the `force` flag.
- **High score today** is still browser `localStorage`; the server leg is
  tracked work (see Part D).

## Prerequisites

- Node 24 (see `.nvmrc`), dependencies installed (`npm install`).
- Rust toolchain with the wasm32 target **only** to rebuild the signer stub:
  `rustup target add wasm32-unknown-unknown`. Without it, `npm run build`
  warns and continues — the game runs without the stub.
- A Cloudflare account (free) and a Telegram account.

## Part A — Configure the code

1. `cp .env.example .env`. Nothing in the client needs a secret; the file is
   reserved for server/bot work. Never commit `.env`.
2. Check `wrangler.toml`: `name = "khanqah-rush"` becomes
   `https://khanqah-rush.<your-account>.workers.dev`. Rename it now if you
   want a different subdomain (lowercase, dashes only).
3. No bot token and no game short name go into the client. The share flow
   uses the live page URL at runtime (Games share button work is tracked
   separately — the page must include `https://telegram.org/js/games.js`
   and call `TelegramGameProxy.shareScore()` from a user gesture).
4. Sanity-build: `npm run build`, then `npm test` and `npm run lint`.
   Checkpoint: `dist/index.html` exists and references `assets/`.

## Part B — Deploy the game page to Cloudflare Workers

1. Log in once: `npx wrangler login`.
2. Deploy: `npm run deploy` (builds, then uploads `dist/` as static assets).
   Validate the config without credentials any time:
   `npx wrangler deploy --dry-run` (expect "No bindings found" — that
   confirms no KV/storage is used).
3. Copy the `https://khanqah-rush.<account>.workers.dev` URL and open it in
   a desktop browser.
   Checkpoint: start menu renders, one chop works per side (mouse/touch and
   keyboard `A`/`D`), game over + play-again cycle works.
4. Optional custom domain (still free): add the domain to your Cloudflare
   account and add a `routes` entry to `wrangler.toml`; redeploy. The
   workers.dev URL keeps working either way.

## Part C — Register bot and Game with BotFather

Do this in a chat with [@BotFather](https://t.me/BotFather), in order.
Accept the gaming terms when prompted (required per game).

1. **Create the bot**: `/newbot` → display name → username (must end in
   `bot`). BotFather replies with the **bot token**. Store it in a password
   manager — it only ever lives server-side (Worker secret, see Part D).
2. **Register the Game**: `/newgame` → select your bot → title →
   description → **photo** → optional gameplay **GIF** (attracts players;
   the legacy Lumberjack-style GIF is the model) → the **short name**
   (letters, digits, underscores — this is the Game ID, e.g.
   `khanqah_rush`). There is **no URL field here**: the game URL is answered
   per launch by your server (Part D).
3. Manage later with `/mybots` → your bot → (game settings). Keep the photo
   and description fresh; `telegram_game_banner.png` in the repo root is a
   candidate source asset.

## Part D — Run the bot server (launch URL + scores)

A small server is mandatory: Telegram calls it on Play, and only it may call
score methods with the bot token. It can live in the **same** Cloudflare
Worker (fetch handler + static assets, still no KV — Telegram stores the
scores). Status: **implemented** — `worker/index.js` (production entry: webhook +
score API over `server/score-core.js`, static fallback via the assets
binding) with `server/example.cjs` kept as the local-dev reference.
Remaining: production hardening (monitoring/review per
`docs/anticheat-future.md` layer 7), your BotFather registration + secrets
below, and setting the webhook (Part E).

| Endpoint / trigger | Action |
|---|---|
| `answerCallbackQuery` on game callback query | Reply with `url` = your Part B URL (+ signed per-user params later). Without this answer, Play does nothing. |
| `POST /api/setScore` from the game page | Validate, then Bot API `setGameScore(chat_id, message_id, user_id, score)`. Use `force=true` only to demote cheaters. |
| Game-over tables (optional) | Bot API `getGameHighScores` for in-game leaderboards. |

- Secrets: `wrangler secret put TELEGRAM_BOT_TOKEN` (never in code/env files);
  `SERVER_SECRET` signs launch tokens (defaults to the bot token for local dev).
- Tracked follow-ups: production hardening, Worker entry adapter, and the
  client Games adaptation (`games.js`, `TelegramGameProxy.shareScore()`).

## Part E — Launch and verify in Telegram

1. From your bot, `sendGame(game_short_name)` to a test chat (or via inline
   mode). The message shows a Play button.
2. Press Play on a real device (Android/iOS app; desktop works too but test
   mobile): the game must open at your Part B URL.
3. Playtest checklist:
   - Start menu shows over the canvas; `Start Chopping` hides it.
   - Left/right chops respond to touch zones and `A`/`D` on desktop.
   - Stamina drains, rejuvenation gauge fills, game over appears on branch
     hit or exhaustion; `Chop Again` restarts; best score persists.
   - Once Part D exists: submit a score, confirm the scoreboard updates and
     a record triggers the chat service message; confirm the share button.
   - Sound toggle works; voice toggle stays a no-op by design
     (see `PROJECT_RULES.md`).
4. Each deploy repeats Parts B→E: `npm run deploy`, then re-open the game
   (kill the old WebView instance first — Telegram may cache the page).

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Play button does nothing | Nothing answered the callback query — Part D server missing or webhook not set. |
| Blank game page, works in browser | URL is not HTTPS, or Telegram cached an old answered URL — redeploy, re-answer, fully close/reopen the WebView. |
| Scores never update | Game page has no server to POST to yet (Part D), or the server lacks the bot token secret. |
| `signer.wasm` 404 in console | Normal in stub phase if `wasm:build` was skipped (no Rust); the loader degrades gracefully. |
| `wrangler` auth errors | `npx wrangler login` again; check with `npx wrangler whoami`. |
| Fonts look wrong | Google Fonts links in `index.html` need network; falls back to system fonts offline. |

## Costs

Workers free tier (100k requests/day) + static assets + no KV/storage +
workers.dev subdomain = 0 cost. Bot API usage (sendGame, setGameScore,
answerCallbackQuery) is free. The only paid-adjacent item is an optional
custom domain (Cloudflare zone, itself free for DNS).
