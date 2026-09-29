// Reference bot server for Khanqah Rush (Telegram Games platform).
//
// REFERENCE ONLY — not wired into the game yet. Entry point for the
// signed-score task. Runs on plain Node.js, no dependencies:
//
//   TELEGRAM_BOT_TOKEN=... GAME_URL=https://... GAME_SHORT_NAME=... node server/example.cjs
//
// Contract (see docs/DEPLOYMENT.md Part D):
// - Telegram → POST /telegram-webhook (updates). Verify the
//   X-Telegram-Bot-Api-Secret-Token header when WEBHOOK_SECRET is set.
// - Game launch: answer the Play callback query with the game URL.
// - Scores: game page → POST /api/setScore → Bot API setGameScore.
//   Telegram stores the board and announces records; force-demote cheaters.
const http = require("node:http");

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const GAME_URL = process.env.GAME_URL || "";
const GAME_SHORT_NAME = process.env.GAME_SHORT_NAME || "khanqah_rush";
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || "";
const PORT = Number(process.env.PORT) || 3000;

const TELEGRAM_API = `https://api.telegram.org/bot${BOT_TOKEN}`;

async function telegram(method, params) {
	const res = await fetch(`${TELEGRAM_API}/${method}`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(params),
	});
	return res.json();
}

function readJson(req) {
	return new Promise((resolve, reject) => {
		let raw = "";
		req.on("data", (chunk) => {
			raw += chunk;
		});
		req.on("end", () => {
			try {
				resolve(raw ? JSON.parse(raw) : {});
			} catch (err) {
				reject(err);
			}
		});
		req.on("error", reject);
	});
}

function json(res, status, body) {
	res.writeHead(status, { "Content-Type": "application/json" });
	res.end(JSON.stringify(body));
}

const server = http.createServer(async (req, res) => {
	try {
		if (req.method === "GET" && req.url === "/healthz") {
			return json(res, 200, { ok: true });
		}

		if (req.method === "POST" && req.url === "/telegram-webhook") {
			if (
				WEBHOOK_SECRET &&
				req.headers["x-telegram-bot-api-secret-token"] !== WEBHOOK_SECRET
			) {
				return json(res, 401, { ok: false });
			}
			const update = await readJson(req);
			const query = update.callback_query;
			if (query?.game_short_name === GAME_SHORT_NAME) {
				// Answer Play with the game URL (per-user signed params go here later).
				await telegram("answerCallbackQuery", {
					callback_query_id: query.id,
					url: GAME_URL,
				});
			}
			return json(res, 200, { ok: true });
		}

		if (req.method === "POST" && req.url === "/api/setScore") {
			const { user_id, chat_id, message_id, score } = await readJson(req);
			const clean = Math.max(0, Math.floor(Number(score) || 0));
			// TODO (signed-score task): verify launch token + HMAC envelope
			// and plausibility before writing. Always 200 so probes learn nothing.
			if (BOT_TOKEN && user_id && chat_id && message_id) {
				await telegram("setGameScore", {
					user_id,
					chat_id,
					message_id,
					score: clean,
				});
			}
			return json(res, 200, { ok: true, score: clean });
		}

		return json(res, 404, { ok: false });
	} catch (err) {
		console.error(err);
		return json(res, 500, { ok: false });
	}
});

server.listen(PORT, () => {
	console.log(`Score server listening on :${PORT} (game: ${GAME_SHORT_NAME})`);
});
