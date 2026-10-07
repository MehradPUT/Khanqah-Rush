import { createHash, createHmac, randomBytes } from "node:crypto";
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { describe, expect, it, vi } from "vitest";
import {
	deriveSessionKey,
	packTrace,
	replayTrace,
	splitSeedHex,
} from "../server/score-core.js";
import worker from "../worker/index.js";

let simWasmBytes = null;
async function wasmBytesOrNull() {
	if (!simWasmBytes) {
		if (!existsSync("public/wasm/sim.wasm")) {
			return null;
		}
		simWasmBytes = await readFile("public/wasm/sim.wasm");
	}
	return simWasmBytes;
}

const ENV = {
	TELEGRAM_BOT_TOKEN: "test-token",
	SERVER_SECRET: "test-secret",
	GAME_SHORT_NAME: "khanqah_rush",
	GAME_URL: "https://game.test",
	WEBHOOK_SECRET: "wh-secret",
	ASSETS: {
		fetch: async (req) => {
			const url = new URL(req.url);
			if (url.pathname === "/wasm/sim.wasm") {
				const bytes = await wasmBytesOrNull();
				if (bytes) {
					return new Response(bytes, {
						headers: { "Content-Type": "application/wasm" },
					});
				}
			}
			return new Response("assets", { status: 200 });
		},
	},
};

function post(path, body, headers = {}) {
	return new Request(`https://game.test${path}`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...headers },
		body: JSON.stringify(body),
	});
}

async function traceFields(seedHex) {
	const { seedLo, seedHi } = splitSeedHex(seedHex);
	const raw = packTrace({
		seedLo,
		seedHi,
		chops: [{ side: 0, t: 100 }],
		endTimeMs: 200,
	});
	const bytes = Buffer.from(raw);
	return {
		trace: bytes.toString("base64"),
		traceHash: createHash("sha256").update(bytes).digest("hex"),
	};
}

/**
 * Play a fixed alternating script against the session seed, learn the
 * replayed outcome locally, then submit it. Returns the worker response
 * plus what a correct server must write. Skips (null) without artifacts.
 */
async function submitReplayed({ lt, sid, key, seedHex }) {
	const wasmBytes = await wasmBytesOrNull();
	if (!wasmBytes) {
		return null;
	}
	const { seedLo, seedHi } = splitSeedHex(seedHex);
	const chops = [];
	let t = 0;
	for (let i = 0; i < 60; i++) {
		t += 200;
		chops.push({ side: i % 2 === 0 ? 0 : 1, t });
	}
	const raw = packTrace({ seedLo, seedHi, chops, endTimeMs: t });
	const bytes = Buffer.from(raw);
	const trace = bytes.toString("base64");
	const traceHash = createHash("sha256").update(bytes).digest("hex");
	const learned = await replayTrace({
		traceB64: trace,
		wasmBytes,
		claimed: { score: -1, alive: true },
		serverSecret: "test-secret",
		sessionId: sid,
	});
	if (learned.ok || !learned.replayed) {
		throw new Error("expected a mismatch probe to reveal the outcome");
	}
	const { score, survivalMs } = learned.replayed;
	// Duration derived from the trace itself so plausibility is
	// structurally consistent (score <= chops <= ceil(duration * rate)).
	const durationSec = Math.max(1, Math.ceil(survivalMs / 1000));
	const nonce = randomBytes(16).toString("hex");
	const timestamp = Math.floor(Date.now() / 1000);
	const canonical = [
		"khanqah-v2",
		sid,
		String(score),
		String(durationSec),
		nonce,
		String(timestamp),
		traceHash,
	].join("\n");
	const tag = createHmac("sha256", Buffer.from(key))
		.update(canonical)
		.digest("hex");
	const response = await worker.fetch(
		post("/api/setScore", {
			lt,
			sid,
			score,
			durationSec,
			nonce,
			timestamp,
			tag,
			trace,
			traceHash,
		}),
		{ ...ENV },
	);
	return { response, score };
}

async function signedBody({ lt, sid, key, score, durationSec, seedHex }) {
	const { randomBytes } = await import("node:crypto");
	const nonce = randomBytes(16).toString("hex");
	const timestamp = Math.floor(Date.now() / 1000);
	const { trace, traceHash } = await traceFields(seedHex);
	const canonical = [
		"khanqah-v2",
		sid,
		String(score),
		String(durationSec),
		nonce,
		String(timestamp),
		traceHash,
	].join("\n");
	const tag = createHmac("sha256", Buffer.from(key))
		.update(canonical)
		.digest("hex");
	return {
		lt,
		sid,
		score,
		durationSec,
		nonce,
		timestamp,
		tag,
		trace,
		traceHash,
	};
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
		seed: url.searchParams.get("seed"),
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

	it("answers /start by sending the game message", async () => {
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
			// The game message carries Telegram's own working Play button —
			// no custom buttons (callback_game is game-message-only).
			const sent = telegramMock.mock.calls.find(([url]) =>
				url.endsWith("/sendGame"),
			);
			expect(sent).toBeTruthy();
			expect(JSON.parse(sent[1].body)).toEqual({
				chat_id: 8,
				game_short_name: "khanqah_rush",
			});
			expect(
				telegramMock.mock.calls.filter(([url]) => url.endsWith("/sendMessage"))
					.length,
			).toBe(0);
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it("falls back to plain text when sendGame is rejected", async () => {
		const telegramMock = vi.fn(async (url) => {
			if (url.endsWith("/sendGame")) {
				return new Response(
					JSON.stringify({ ok: false, description: "Bad Request: rejected" }),
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
			expect(sends.length).toBe(1);
			const fallback = JSON.parse(sends[0][1].body);
			expect(fallback.reply_markup).toBeUndefined();
			expect(fallback.text).toContain("@KhanqahRushBot");
		} finally {
			vi.unstubAllGlobals();
		}
	});

	it("answers the legacy board fetch with an empty board", async () => {
		const res = await worker.fetch(
			post("/api/getHighScores", { data: "legacy-session" }),
			{ ...ENV },
		);
		expect(res.status).toBe(200);
		expect(await res.json()).toEqual({ ok: true, scores: [] });
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
			const { lt, sid, sk, seed } = await launchViaWebhook(telegramMock);
			expect(lt && sid && sk && seed).toBeTruthy();

			const key = await deriveSessionKey("test-secret", sid);
			const callsBefore = telegramMock.mock.calls.length;
			const played = await submitReplayed({ lt, sid, key, seedHex: seed });
			if (!played) {
				return;
			}
			expect(played.response.status).toBe(200);
			expect(await played.response.clone().json()).toEqual({
				ok: true,
				recorded: true,
			});
			const scoreCalls = telegramMock.mock.calls.filter(([url]) =>
				url.endsWith("/setGameScore"),
			);
			expect(scoreCalls.length).toBe(1);
			expect(JSON.parse(scoreCalls[0][1].body)).toMatchObject({
				user_id: 7,
				chat_id: 8,
				message_id: 9,
				score: played.score,
			});

			// Inflated claim on a valid session: still HTTP 200 (silent),
			// but no Telegram write.
			const badBody = await signedBody({
				lt,
				sid,
				key,
				score: played.score + 1000,
				durationSec: 30,
				seedHex: seed,
			});
			const bad = await worker.fetch(post("/api/setScore", badBody), {
				...ENV,
			});
			expect(bad.status).toBe(200);
			// TEMP-DEBUG: debugReason rides along until verified; match loosely.
			expect(await bad.json()).toMatchObject({ ok: true, recorded: false });
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
			const seed = url.searchParams.get("seed");
			expect(lt && sid && sk && seed).toBeTruthy();

			const key = await deriveSessionKey("test-secret", sid);
			const played = await submitReplayed({ lt, sid, key, seedHex: seed });
			if (!played) {
				return;
			}
			expect(played.response.status).toBe(200);
			expect(await played.response.clone().json()).toEqual({
				ok: true,
				recorded: true,
			});
			const scoreCalls = telegramMock.mock.calls.filter(([url]) =>
				url.endsWith("/setGameScore"),
			);
			expect(scoreCalls.length).toBe(1);
			expect(JSON.parse(scoreCalls[0][1].body)).toMatchObject({
				user_id: 7,
				inline_message_id: "AAQAAxkBAAI",
				score: played.score,
			});
		} finally {
			vi.unstubAllGlobals();
		}
	});
});
