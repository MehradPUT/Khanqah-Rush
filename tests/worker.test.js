import { createHmac } from "node:crypto";
import { describe, expect, it, vi } from "vitest";
import { deriveSessionKey } from "../server/score-core.js";
import worker from "../worker/index.js";

const ENV = {
	TELEGRAM_BOT_TOKEN: "test-token",
	SERVER_SECRET: "test-secret",
	GAME_SHORT_NAME: "khanqah_rush",
	GAME_URL: "https://game.test",
	WEBHOOK_SECRET: "wh-secret",
	ASSETS: { fetch: async () => new Response("assets", { status: 200 }) },
};

function post(path, body, headers = {}) {
	return new Request(`https://game.test${path}`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...headers },
		body: JSON.stringify(body),
	});
}

async function launchViaWebhook(telegramMock) {
	const update = {
		callback_query: {
			id: "q1",
			game_short_name: "khanqah_rush",
			from: { id: 7 },
			message: { chat: { id: 8 }, message_id: 9 },
		},
	};
	const res = await worker.fetch(
		post("/telegram-webhook", update, {
			"X-Telegram-Bot-Api-Secret-Token": "wh-secret",
		}),
		{ ...ENV },
	);
	expect(res.status).toBe(200);
	const answer = telegramMock.mock.calls.find(([url]) =>
		url.endsWith("/answerCallbackQuery"),
	);
	expect(answer).toBeTruthy();
	const params = JSON.parse(answer[1].body);
	const url = new URL(params.url);
	return {
		lt: url.searchParams.get("lt"),
		sid: url.searchParams.get("sid"),
		sk: url.searchParams.get("sk"),
	};
}

describe("worker entry", () => {
	it("answers inline queries with the game", async () => {
		const telegramMock = vi.fn(
			async () => new Response(JSON.stringify({ ok: true })),
		);
		vi.stubGlobal("fetch", telegramMock);
		try {
			const res = await worker.fetch(
				post(
					"/telegram-webhook",
					{ inline_query: { id: "iq1", query: "kha" } },
					{},
				),
				{ ...ENV, WEBHOOK_SECRET: "" },
			);
			expect(res.status).toBe(200);
			const answer = telegramMock.mock.calls.find(([url]) =>
				url.endsWith("/answerInlineQuery"),
			);
			expect(answer).toBeTruthy();
			const params = JSON.parse(answer[1].body);
			expect(params.inline_query_id).toBe("iq1");
			expect(params.results).toEqual([
				{ type: "game", id: "iq1", game_short_name: "khanqah_rush" },
			]);
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it("replies to /start with a Play button", async () => {
		const telegramMock = vi.fn(
			async () => new Response(JSON.stringify({ ok: true })),
		);
		vi.stubGlobal("fetch", telegramMock);
		try {
			const res = await worker.fetch(
				post(
					"/telegram-webhook",
					{ message: { chat: { id: 8 }, text: "/start" } },
					{},
				),
				{ ...ENV, WEBHOOK_SECRET: "" },
			);
			expect(res.status).toBe(200);
			const sent = telegramMock.mock.calls.find(([url]) =>
				url.endsWith("/sendMessage"),
			);
			expect(sent).toBeTruthy();
			const params = JSON.parse(sent[1].body);
			expect(params.chat_id).toBe(8);
			expect(params.reply_markup.inline_keyboard[0][0].callback_game).toEqual(
				{},
			);
			// No fallback: exactly one send.
			expect(
				telegramMock.mock.calls.filter(([url]) => url.endsWith("/sendMessage"))
					.length,
			).toBe(1);
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it("degrades to plain text when the rich /start reply is rejected", async () => {
		const telegramMock = vi.fn(async (url) => {
			if (url.endsWith("/sendMessage")) {
				const calls = telegramMock.mock.calls.length;
				return new Response(
					JSON.stringify(
						calls === 1
							? { ok: false, description: "Bad Request: rejected" }
							: { ok: true },
					),
				);
			}
			return new Response(JSON.stringify({ ok: true }));
		});
		vi.stubGlobal("fetch", telegramMock);
		try {
			const res = await worker.fetch(
				post(
					"/telegram-webhook",
					{ message: { chat: { id: 8 }, text: "/start" } },
					{},
				),
				{ ...ENV, WEBHOOK_SECRET: "" },
			);
			expect(res.status).toBe(200);
			const sends = telegramMock.mock.calls.filter(([url]) =>
				url.endsWith("/sendMessage"),
			);
			expect(sends.length).toBe(2);
			const fallback = JSON.parse(sends[1][1].body);
			expect(fallback.reply_markup).toBeUndefined();
			expect(fallback.text).toContain("@KhanqahRushBot");
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it("serves health and falls through to assets", async () => {
		const health = await worker.fetch(
			new Request("https://game.test/healthz"),
			{
				...ENV,
			},
		);
		expect(health.status).toBe(200);
		const page = await worker.fetch(new Request("https://game.test/"), {
			...ENV,
		});
		expect(await page.text()).toBe("assets");
	});

	it("rejects webhook calls with a bad secret", async () => {
		const res = await worker.fetch(post("/telegram-webhook", {}), { ...ENV });
		expect(res.status).toBe(401);
	});

	it("answers Play with a session-minted URL and writes only valid scores", async () => {
		const telegramMock = vi.fn(
			async () => new Response(JSON.stringify({ ok: true })),
		);
		vi.stubGlobal("fetch", telegramMock);
		try {
			const { lt, sid, sk } = await launchViaWebhook(telegramMock);
			expect(lt && sid && sk).toBeTruthy();

			const key = await deriveSessionKey("test-secret", sid);
			const { randomBytes } = await import("node:crypto");
			async function submit(score, nonceHex) {
				const timestamp = Math.floor(Date.now() / 1000);
				const canonical = [
					"khanqah-v1",
					sid,
					String(score),
					"30",
					nonceHex,
					String(timestamp),
				].join("\n");
				const tag = createHmac("sha256", Buffer.from(key))
					.update(canonical)
					.digest("hex");
				return worker.fetch(
					post("/api/setScore", {
						lt,
						sid,
						score,
						durationSec: 30,
						nonce: nonceHex,
						timestamp,
						tag,
					}),
					{ ...ENV },
				);
			}

			const callsBefore = telegramMock.mock.calls.length;
			const okRes = await submit(120, randomBytes(16).toString("hex"));
			expect(okRes.status).toBe(200);
			const scoreCalls = telegramMock.mock.calls.filter(([url]) =>
				url.endsWith("/setGameScore"),
			);
			expect(scoreCalls.length).toBe(1);
			expect(JSON.parse(scoreCalls[0][1].body)).toMatchObject({
				user_id: 7,
				chat_id: 8,
				message_id: 9,
				score: 120,
			});

			// Tampered score: still HTTP 200 (silent), but no Telegram write.
			const bad = await submit(99999, randomBytes(16).toString("hex"));
			expect(bad.status).toBe(200);
			expect(
				telegramMock.mock.calls.filter(([url]) => url.endsWith("/setGameScore"))
					.length,
			).toBe(1);
			expect(telegramMock.mock.calls.length).toBe(callsBefore + 1);
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it("mints sessions for inline launches and writes via inline_message_id", async () => {
		const telegramMock = vi.fn(
			async () => new Response(JSON.stringify({ ok: true })),
		);
		vi.stubGlobal("fetch", telegramMock);
		try {
			const res = await worker.fetch(
				post(
					"/telegram-webhook",
					{
						callback_query: {
							id: "q9",
							game_short_name: "khanqah_rush",
							from: { id: 7 },
							inline_message_id: "AAQAAxkBAAI",
						},
					},
					{ "X-Telegram-Bot-Api-Secret-Token": "wh-secret" },
				),
				{ ...ENV },
			);
			expect(res.status).toBe(200);
			const answer = telegramMock.mock.calls.find(([url]) =>
				url.endsWith("/answerCallbackQuery"),
			);
			const params = JSON.parse(answer[1].body);
			const url = new URL(params.url);
			const lt = url.searchParams.get("lt");
			const sid = url.searchParams.get("sid");
			const sk = url.searchParams.get("sk");
			expect(lt && sid && sk).toBeTruthy();

			const key = await deriveSessionKey("test-secret", sid);
			const { randomBytes } = await import("node:crypto");
			const nonce = randomBytes(16).toString("hex");
			const timestamp = Math.floor(Date.now() / 1000);
			const canonical = [
				"khanqah-v1",
				sid,
				"60",
				"20",
				nonce,
				String(timestamp),
			].join("\n");
			const tag = createHmac("sha256", Buffer.from(key))
				.update(canonical)
				.digest("hex");
			const posted = await worker.fetch(
				post("/api/setScore", {
					lt,
					sid,
					score: 60,
					durationSec: 20,
					nonce,
					timestamp,
					tag,
				}),
				{ ...ENV },
			);
			expect(posted.status).toBe(200);
			const scoreCalls = telegramMock.mock.calls.filter(([url]) =>
				url.endsWith("/setGameScore"),
			);
			expect(scoreCalls.length).toBe(1);
			expect(JSON.parse(scoreCalls[0][1].body)).toMatchObject({
				user_id: 7,
				inline_message_id: "AAQAAxkBAAI",
				score: 60,
			});
		} finally {
			vi.unstubAllGlobals();
		}
	});
});
