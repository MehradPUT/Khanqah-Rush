# Deployment

End-to-end guide: configure the code, host it on Cloudflare Workers (free,
no storage), register the bot and Mini App with BotFather, and verify.
Follow top to bottom; each part ends with a checkpoint.

## What is being deployed

- **Frontend only.** `npm run build` emits `dist/` (single-page app + WASM
  stub) and Cloudflare Workers serves it as static files over HTTPS.
- **Telegram Mini App, not legacy Games.** This project is a Web App opened
  inside Telegram (`src/telegram/tma.ts`, `telegram-web-app.js`). It does
  **not** use the old Bot API Games platform (`/newgame`, `setGameScore`),
  so there is no game-scores API involved. The "Game ID" in this guide is the
  Mini App **short name** you choose in BotFather (`/newapp`), which becomes
  the direct link `https://t.me/<bot>/<short-name>`.
- **Scores are local-only today.** The high score lives in the browser's
  `localStorage`; there is no score server yet. Server-side verification is
  tracked future work (see `docs/anticheat-future.md`).

## Prerequisites

- Node 24 (see `.nvmrc`), dependencies installed (`npm install`).
- Rust toolchain with the wasm32 target **only** if you want to rebuild the
  signer stub: `rustup target add wasm32-unknown-unknown`. Without it,
  `npm run build` warns and continues — the game runs without the stub.
- A Cloudflare account (free) and a Telegram account.

## Part A — Configure the code

1. `cp .env.example .env`. Nothing in the client needs a secret today; the
   file is reserved for future server/bot work. Never commit `.env`.
2. Check `wrangler.toml`: `name = "khanqah-rush"` becomes
   `https://khanqah-rush.<your-account>.workers.dev`. Rename it now if you
   want a different subdomain (lowercase, dashes only).
3. No bot token goes into the code. The share button builds its link from
   `window.location.href` at runtime, so it automatically points at whatever
   URL Telegram opens the app from.
4. Sanity-build: `npm run build`, then `npm test` and `npm run lint`.
   Checkpoint: `dist/index.html` exists and references `assets/`.

## Part B — Deploy to Cloudflare Workers

1. Log in once: `npx wrangler login`.
2. Deploy: `npm run deploy` (builds, then uploads `dist/` as static assets).
   Dry-run the config any time without credentials:
   `npx wrangler deploy --dry-run` (expect "No bindings found" — that
   confirms no KV/storage is used).
3. Copy the `https://khanqah-rush.<account>.workers.dev` URL from the output
   and open it in a desktop browser.
   Checkpoint: start menu renders, one chop works per side (mouse/touch and
   keyboard `A`/`D`), game over + play-again cycle works.
4. Optional custom domain (still free): add the domain to your Cloudflare
   account and add a `routes` entry to `wrangler.toml`; redeploy. The
   workers.dev URL keeps working either way.

## Part C — Register bot and Mini App with BotFather

Do this in a chat with [@BotFather](https://t.me/BotFather), in order:

1. **Create the bot**: `/newbot` → pick a display name → pick a username
   (must end in `bot`). BotFather replies with the **bot token**.
   Store it in a password manager — it never goes into this repo.
2. **Register the Mini App**: `/newapp` → select your bot → title →
   description → **640×360 photo** (`telegram_game_banner.png` in the repo
   root is the candidate; resize/crop to exactly 640×360 if needed) →
   paste the **HTTPS** workers.dev URL from Part B → choose the **short
   name** (letters, digits, underscores — this is the Game ID).
   BotFather replies with the direct link `https://t.me/<bot>/<short-name>`.
3. **Menu button (recommended)**: `/setmenubutton` → select your bot →
   paste the same URL → button title (e.g. "Play"). Every chat with the bot
   now shows the game behind the menu button.
4. Manage later with `/myapps` (edit title/description/photo/URL). If you
   redeploy to a new URL, update it here — Telegram caches the old one.

## Part D — Wire up and verify in Telegram

1. Open the direct link or the bot's menu button on a real device
   (Android/iOS Telegram app — the desktop client works too but test mobile).
2. Playtest checklist:
   - Start menu shows over the canvas; `Start Chopping` hides it.
   - Left/right chops respond to touch zones and `A`/`D` on desktop.
   - Stamina drains, rejuvenation gauge fills, game over appears on branch
     hit or exhaustion; `Chop Again` restarts; best score persists.
   - `Share Score` opens a `t.me/share` link (uses the live page URL).
   - Sound toggle works; voice toggle stays a no-op by design
     (see `PROJECT_RULES.md`).
3. Each deploy repeats Parts B→D: `npm run deploy`, then re-open the Mini
   App (kill the old WebView instance first — Telegram may cache the page).

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Blank page in Telegram, works in browser | URL is not HTTPS, or an old URL is cached — update via `/myapps` and fully close/reopen the WebView. |
| Old version after redeploy | Telegram/WebView cache — close the Mini App completely and reopen; bump nothing, just retry. |
| `signer.wasm` 404 in console | Normal in stub phase if `wasm:build` was skipped (no Rust); the loader degrades gracefully. Rebuild with the wasm32 target to silence it. |
| `wrangler` auth errors | Run `npx wrangler login` again; check the active account with `npx wrangler whoami`. |
| Fonts look wrong | Google Fonts links in `index.html` need network; the game falls back to system fonts offline. |

## Costs

Workers free tier (100k requests/day) + static assets + no KV/storage +
workers.dev subdomain = 0 cost. The only paid-adjacent item is an optional
custom domain (needs a Cloudflare zone, itself free for DNS).
