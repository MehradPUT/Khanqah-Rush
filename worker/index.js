/**
 * Production Cloudflare Worker entry for Khanqah Rush.
 *
 * Same contract as server/example.cjs (see docs/DEPLOYMENT.md Part D), but
 * running on the edge next to the static game: webhook + score API handled
 * here, everything else falls through to the Workers Static Assets binding.
 * Secrets arrive via env (wrangler secret put); stateless per isolate —
 * the nonce store is in-memory, so cross-isolate replays are a documented
 * limitation until a shared store exists.
 */
import {
	buildSetGameScoreCall,
	checkPlausibility,
	createMemoryNonceStore,
	deriveSessionKey,
	issueLaunchToken,
	verifyEnvelope,
	verifyLaunchToken,
} from "../server/score-core.js";

const nonceStore = createMemoryNonceStore();

function randomSessionId() {
	const bytes = crypto.getRandomValues(new Uint8Array(16));
	return Array.from(bytes)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

function toHex(bytes) {
	return Array.from(bytes)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

function json(body, status = 200) {
	return Response.json(body, { status });
}

async function telegram(env, method, params) {
	const res = await fetch(
		`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(params),
		},
	);
	const data = await res.json().catch(() => ({}));
	if (!data.ok) {
		console.warn(`[worker] telegram ${method} failed`, JSON.stringify(data));
	}
	return data;
}

function serverSecret(env) {
	return env.SERVER_SECRET || env.TELEGRAM_BOT_TOKEN;
}

async function handleUpdate(update, req, env) {
	if (env.WEBHOOK_SECRET) {
		const got = req.headers.get("x-telegram-bot-api-secret-token");
		// Timing-safe compare without node:crypto (Workers-safe).
		const a = new TextEncoder().encode(got ?? "");
		const b = new TextEncoder().encode(env.WEBHOOK_SECRET);
		let diff = a.length === b.length ? 0 : 1;
		const n = Math.max(a.length, b.length);
		for (let i = 0; i < n; i++) {
			diff |= (a[i] ?? 0) ^ (b[i] ?? 0);
		}
		if (diff !== 0) {
			return json({ ok: false }, 401);
		}
	}
	if (update.inline_query) {
		// Inline mode: answer with the game so typing @botname offers it.
		// Requires /setinline on the bot (BotFather); without it Telegram
		// never sends these updates and the inline list spins forever.
		if (env.TELEGRAM_BOT_TOKEN) {
			await telegram(env, "answerInlineQuery", {
				inline_query_id: update.inline_query.id,
				results: [
					{
						type: "game",
						id: update.inline_query.id,
						game_short_name: env.GAME_SHORT_NAME,
					},
				],
			});
		}
		return json({ ok: true });
	}
	if (
		typeof update.message?.text === "string" &&
		update.message.text.startsWith("/start")
	) {
		if (env.TELEGRAM_BOT_TOKEN) {
			// The entry point is a real game message: Telegram gives it a
			// working Play button automatically. (callback_game buttons are
			// only valid on game messages, and game links use ?game= form —
			// a URL button to t.me/... goes nowhere.)
			const sent = await telegram(env, "sendGame", {
				chat_id: update.message.chat.id,
				game_short_name: env.GAME_SHORT_NAME,
			});
			if (!sent.ok) {
				const handle = env.BOT_USERNAME || "KhanqahRushBot";
				await telegram(env, "sendMessage", {
					chat_id: update.message.chat.id,
					text: `🪓 Khanqah Rush is live! Type @${handle} in any chat to play inline.`,
				});
			}
		}
		return json({ ok: true });
	}
	const query = update.callback_query;
	if (query?.game_short_name === env.GAME_SHORT_NAME) {
		const origin = new URL(req.url).origin;
		const gameUrl = env.GAME_URL || origin;
		let url = gameUrl;
		const userId = query.from?.id;
		const chatId = query.message?.chat?.id;
		const messageId = query.message?.message_id;
		const inlineMessageId = query.inline_message_id;
		const launchIds =
			Number.isInteger(userId) &&
			(Number.isInteger(chatId) && Number.isInteger(messageId)
				? { userId, chatId, messageId }
				: typeof inlineMessageId === "string"
					? { userId, inlineMessageId }
					: null);
		if (launchIds) {
			const sessionId = randomSessionId();
			const lt = await issueLaunchToken(launchIds, serverSecret(env));
			const sk = toHex(await deriveSessionKey(serverSecret(env), sessionId));
			const sep = gameUrl.includes("?") ? "&" : "?";
			url =
				`${gameUrl}${sep}lt=${encodeURIComponent(lt)}` +
				`&sid=${sessionId}&sk=${sk}`;
		}
		if (env.TELEGRAM_BOT_TOKEN) {
			await telegram(env, "answerCallbackQuery", {
				callback_query_id: query.id,
				url,
			});
		}
	}
	return json({ ok: true });
}

async function handleSetScore(req, env) {
	const body = await req.json().catch(() => ({}));
	// Always 200 so probes learn nothing; reasons stay server-side.
	const launch = await verifyLaunchToken(body.lt, serverSecret(env));
	if (!launch) {
		return json({ ok: true });
	}
	const verified = await verifyEnvelope(
		{
			sessionId: body.sid,
			score: body.score,
			durationSec: body.durationSec,
			nonce: body.nonce,
			timestamp: body.timestamp,
			tag: body.tag,
		},
		{ serverSecret: serverSecret(env), nonceStore },
	);
	if (!verified.ok) {
		return json({ ok: true });
	}
	const plausible = checkPlausibility({
		score: body.score,
		durationSec: body.durationSec,
	});
	if (!plausible.ok) {
		return json({ ok: true });
	}
	if (env.TELEGRAM_BOT_TOKEN) {
		const call = buildSetGameScoreCall({
			userId: launch.u,
			chatId: launch.c,
			messageId: launch.m,
			inlineMessageId: launch.i,
			score: body.score,
		});
		await telegram(env, call.method, call.params);
	}
	return json({ ok: true });
}

export default {
	async fetch(req, env) {
		const url = new URL(req.url);
		if (req.method === "GET" && url.pathname === "/healthz") {
			return json({ ok: true });
		}
		if (req.method === "POST" && url.pathname === "/telegram-webhook") {
			const update = await req.json().catch(() => ({}));
			console.log(
				`[worker] update: ${update.inline_query ? "inline_query" : update.callback_query ? "callback_query" : update.message ? `message:${update.message.text ?? "?"}` : "unknown"}`,
			);
			return handleUpdate(update, req, env);
		}
		if (req.method === "POST" && url.pathname === "/api/setScore") {
			return handleSetScore(req, env);
		}
		return env.ASSETS.fetch(req);
	},
};
