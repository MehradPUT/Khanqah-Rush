# Telegram hosting (Cloudflare Workers, free tier)

The Mini App frontend (`dist/`, built by `npm run build`) is served as
Cloudflare Workers static assets — no Worker code, no KV, no storage, so it
stays completely free. See `wrangler.toml`.

## First-time setup

1. Install the CLI (already a devDependency): `npm install`.
2. Log in once: `npx wrangler login`.
3. Build and deploy: `npm run deploy` (runs `npm run build`, which also
   rebuilds the WASM stub via `prebuild`, then `wrangler deploy`).
4. Note the `https://khanqah-rush.<account>.workers.dev` URL from the output.

## Pointing Telegram at it

1. Talk to [@BotFather](https://t.me/BotFather): create the bot (`/newbot`)
   if needed.
2. Attach the Mini App: `/newapp` (or `/setmenubutton` / `/editapp`) and
   paste the workers.dev URL (or your custom domain, see below).
3. Open the game from the bot and playtest: start menu → chop → game over →
   play again. `src/telegram/tma.ts` degrades gracefully outside Telegram.

## Notes

- `.wasm` under `public/wasm/` is served by Workers static assets with the
  correct `application/wasm` content type; nothing to configure.
- Custom domain (optional, still free): add the domain to your Cloudflare
  account, then `npx wrangler deploy` picks up `routes` if you add them to
  `wrangler.toml`. The workers.dev URL keeps working either way.
- Local preview of the production build without deploying:
  `npm run build && npx wrangler dev` (or `npm run preview` for plain Vite).
- Secrets (bot tokens, future signing keys) must never be committed —
  use `wrangler secret put <NAME>` when a Worker-side secret is needed.
  `.env` stays gitignored (see `.env.example`).
