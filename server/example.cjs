// Thin node:http adapter over score-core.js for Khanqah Rush.
// REFERENCE implementation of docs/DEPLOYMENT.md Part D — same logic drops
// into a Cloudflare Worker entry later. Runs on plain Node.js, no
// dependencies (score-core.js itself is dependency-free WebCrypto):
//
//   TELEGRAM_BOT_TOKEN=... GAME_URL=https://... GAME_SHORT_NAME=... \
//     SERVER_SECRET=... node server/example.cjs
//
// SERVER_SECRET signs launch tokens and derives session keys; default is the
// bot token (acceptable for a reference; use a dedicated secret in prod).
const http = require("node:http");
const { randomBytes } = require("node:crypto");
const { join } = require("node:path");
const { pathToFileURL } = require("node:url");

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const SERVER_SECRET = process.env.SERVER_SECRET || BOT_TOKEN;
const GAME_URL = process.env.GAME_URL || "";
const GAME_SHORT_NAME = process.env.GAME_SHORT_NAME || "khanqah_rush";
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || "";
const PORT = Number(process.env.PORT) || 3000;

const TELEGRAM_API = `https://api.telegram.org/bot${BOT_TOKEN}`;

async function main() {
	const core = await import(
		pathToFileURL(join(__dirname, "score-core.js")).href
	);
	const nonceStore = core.createMemoryNonceStore();

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
					let url = GAME_URL;
					const userId = query.from?.id;
					const chatId = query.message?.chat?.id;
					const messageId = query.message?.message_id;
					const inlineMessageId = query.inline_message_id;
					const launchIds =
						Number.isInteger(userId) &&
						(Number.isInteger(chatId) && Number.isInteger(messageId)
							? { userId, chatId, messageId }
							: typeof inlineMessageId === "string" &&
									inlineMessageId.length > 0
								? { userId, inlineMessageId }
								: null);
					if (launchIds) {
						// Mint a launch-bound session: token + session key travel in
						// the answered URL (over TLS). Works for message and inline
						// launches alike.
						const sessionId = randomBytes(16).toString("hex");
						const lt = await core.issueLaunchToken(launchIds, SERVER_SECRET);
						const sk = Buffer.from(
							await core.deriveSessionKey(SERVER_SECRET, sessionId),
						).toString("hex");
						const sep = GAME_URL.includes("?") ? "&" : "?";
						url =
							`${GAME_URL}${sep}lt=${encodeURIComponent(lt)}` +
							`&sid=${sessionId}&sk=${sk}`;
					}
					await telegram("answerCallbackQuery", {
						callback_query_id: query.id,
						url,
					});
				}
				return json(res, 200, { ok: true });
			}

			if (req.method === "POST" && req.url === "/api/setScore") {
				const body = await readJson(req);
				// Always 200 so probes learn nothing; reasons stay server-side.
				const launch = await core.verifyLaunchToken(body.lt, SERVER_SECRET);
				if (!launch) {
					return json(res, 200, { ok: true });
				}
				const verified = await core.verifyEnvelope(
					{
						sessionId: body.sid,
						score: body.score,
						durationSec: body.durationSec,
						nonce: body.nonce,
						timestamp: body.timestamp,
						tag: body.tag,
					},
					{ serverSecret: SERVER_SECRET, nonceStore },
				);
				if (!verified.ok) {
					return json(res, 200, { ok: true });
				}
				const plausible = core.checkPlausibility({
					score: body.score,
					durationSec: body.durationSec,
				});
				if (!plausible.ok) {
					return json(res, 200, { ok: true });
				}
				if (BOT_TOKEN) {
					const call = core.buildSetGameScoreCall({
						userId: launch.u,
						chatId: launch.c,
						messageId: launch.m,
						inlineMessageId: launch.i,
						score: body.score,
					});
					await telegram(call.method, call.params);
				}
				return json(res, 200, { ok: true });
			}

			return json(res, 404, { ok: false });
		} catch (err) {
			console.error(err);
			return json(res, 500, { ok: false });
		}
	});

	server.listen(PORT, () => {
		console.log(
			`Score server listening on :${PORT} (game: ${GAME_SHORT_NAME})`,
		);
	});
}

main().catch((err) => {
	console.error(err);
	process.exit(1);
});
