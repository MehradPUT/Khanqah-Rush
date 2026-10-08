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
	const sessions = core.createSessionRegistry();

	async function telegram(method, params) {
		const res = await fetch(`${TELEGRAM_API}/${method}`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(params),
		});
		return res.json().catch(() => ({}));
	}

	function readJson(req) {
		return new Promise((resolve) => {
			let raw = "";
			req.on("data", (chunk) => {
				raw += chunk;
			});
			req.on("end", () => {
				try {
					resolve(raw ? JSON.parse(raw) : {});
				} catch {
					resolve({});
				}
			});
			req.on("error", () => resolve({}));
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
				if (WEBHOOK_SECRET) {
					// Timing-safe compare without node:crypto (Workers-safe).
					const got = req.headers["x-telegram-bot-api-secret-token"] ?? "";
					const a = Buffer.from(got);
					const b = Buffer.from(WEBHOOK_SECRET);
					let diff = a.length === b.length ? 0 : 1;
					const n = Math.max(a.length, b.length);
					for (let i = 0; i < n; i++) {
						diff |= (a[i] ?? 0) ^ (b[i] ?? 0);
					}
					if (diff !== 0) {
						return json(res, 401, { ok: false });
					}
				}
				const update = await readJson(req);
				const query = update.callback_query;
				if (!GAME_SHORT_NAME || query?.game_short_name !== GAME_SHORT_NAME) {
					return json(res, 200, { ok: true });
				}
				{
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
						// launches alike. Rate-limited launches get the plain URL.
						// The session id is token-bound (isSessionLive at score
						// time), so scoring needs no shared memory.
						const sessionId = randomBytes(16).toString("hex");
						if (sessions.register(userId)) {
							const lt = await core.issueLaunchToken(
								{ ...launchIds, sessionId },
								SERVER_SECRET,
							);
							const sk = Buffer.from(
								await core.deriveSessionKey(SERVER_SECRET, sessionId),
							).toString("hex");
							const seed = await core.deriveSeed(SERVER_SECRET, sessionId);
							const sep = GAME_URL.includes("?") ? "&" : "?";
							url =
								`${GAME_URL}${sep}lt=${encodeURIComponent(lt)}` +
								`&sid=${sessionId}&sk=${sk}&seed=${seed}`;
						}
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
				// Always 200 so probes learn nothing; the recorded flag (also
				// visible on the public leaderboard anyway) tells the game.
				const deny = (reason) => {
					console.warn(`[example] score rejected: ${reason}`);
					return json(res, 200, { ok: true, recorded: false });
				};
				// Fail closed: an empty secret would verify everything under
				// the empty HMAC key.
				if (typeof SERVER_SECRET !== "string" || SERVER_SECRET.length === 0) {
					return deny("no-secret");
				}
				const launch = await core.verifyLaunchToken(body.lt, SERVER_SECRET);
				if (!launch) {
					return deny("bad-launch");
				}
				if (!core.isSessionLive(launch, body.sid)) {
					return deny("stale-session");
				}
				const verified = await core.verifyEnvelope(
					{
						sessionId: body.sid,
						score: body.score,
						durationSec: body.durationSec,
						nonce: body.nonce,
						timestamp: body.timestamp,
						tag: body.tag,
						trace: body.trace,
						traceHash: body.traceHash,
					},
					{ serverSecret: SERVER_SECRET, nonceStore },
				);
				if (!verified.ok) {
					return deny(`envelope-${verified.reason}`);
				}
				const plausible = core.checkPlausibility({
					score: body.score,
					durationSec: body.durationSec,
				});
				if (!plausible.ok) {
					return deny(`plausibility-${plausible.reason}`);
				}
				const replayed = await core.replayTrace({
					traceB64: body.trace,
					claimed: { score: body.score, alive: false },
					serverSecret: SERVER_SECRET,
					sessionId: body.sid,
				});
				if (!replayed.ok) {
					return deny(`replay-${replayed.reason}`);
				}
				if (BOT_TOKEN) {
					const call = core.buildSetGameScoreCall({
						userId: launch.u,
						chatId: launch.c,
						messageId: launch.m,
						inlineMessageId: launch.i,
						score: body.score,
					});
					// Without force, Telegram keeps the higher board score and
					// answers ok:false for a lower one — only a real write
					// counts.
					const written = await telegram(call.method, call.params);
					if (written?.ok) {
						return json(res, 200, { ok: true, recorded: true });
					}
					return deny("telegram-rejected");
				}
				return deny("no-bot-token");
			}

			if (req.method === "POST" && req.url === "/api/getHighScores") {
				await readJson(req).catch(() => ({}));
				return json(res, 200, { ok: true, scores: [] });
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
