import { createHash, createHmac, randomBytes } from "node:crypto";
import { describe, expect, it } from "vitest";
import {
	buildSetGameScoreCall,
	checkPlausibility,
	createMemoryNonceStore,
	createSessionRegistry,
	deflateTrace,
	deriveSeed,
	deriveSessionKey,
	inflateTrace,
	issueLaunchToken,
	packTrace,
	replayTrace,
	sha256Hex,
	timingSafeEqual,
	traceFromB64,
	unpackTrace,
	verifyEnvelope,
	verifyLaunchToken,
} from "../server/score-core.js";

const SECRET = "test-server-secret-please-ignore";
const NOW = 1700000000;

function hex(buf) {
	return Buffer.from(buf).toString("hex");
}

async function validEnvelope(overrides = {}) {
	const sessionId = "sid-test";
	const raw = packTrace({
		seedLo: 9,
		seedHi: 0,
		chops: [{ side: 0, t: 100 }],
		endTimeMs: 200,
	});
	const traceBytes = Buffer.from(await deflateTrace(raw));
	const base = {
		sessionId,
		score: 250,
		durationSec: 42,
		nonce: randomBytes(16).toString("hex"),
		timestamp: NOW,
		trace: traceBytes.toString("base64"),
		traceHash: createHash("sha256").update(traceBytes).digest("hex"),
		...overrides,
	};
	const key = await deriveSessionKey(SECRET, sessionId);
	const canonical = [
		"khanqah-v2",
		base.sessionId,
		String(base.score),
		String(base.durationSec),
		base.nonce,
		String(base.timestamp),
		base.traceHash,
	].join("\n");
	const tag = createHmac("sha256", Buffer.from(key))
		.update(canonical)
		.digest("hex");
	return { ...base, tag };
}

describe("launch tokens", () => {
	it("round-trips message and inline tokens", async () => {
		const token = await issueLaunchToken(
			{ userId: 7, chatId: 8, messageId: 9 },
			SECRET,
			NOW,
		);
		expect(await verifyLaunchToken(token, SECRET, NOW + 10)).toMatchObject({
			u: 7,
			c: 8,
			m: 9,
		});

		const inline = await issueLaunchToken(
			{ userId: 7, inlineMessageId: "AAQAAxkBAAI" },
			SECRET,
			NOW,
		);
		expect(await verifyLaunchToken(inline, SECRET, NOW + 10)).toMatchObject({
			u: 7,
			i: "AAQAAxkBAAI",
		});

		const emptyInline = await issueLaunchToken(
			{ userId: 7, inlineMessageId: "" },
			SECRET,
			NOW,
		);
		expect(await verifyLaunchToken(emptyInline, SECRET, NOW + 10)).toBeNull();
	});

	it("rejects tampered, expired, wrong-secret, and malformed tokens", async () => {
		const token = await issueLaunchToken(
			{ userId: 7, chatId: 8, messageId: 9, ttlSec: 60 },
			SECRET,
			NOW,
		);
		const tampered = token.slice(0, -1) + (token.endsWith("A") ? "B" : "A");
		expect(await verifyLaunchToken(tampered, SECRET, NOW)).toBeNull();
		expect(await verifyLaunchToken(token, SECRET, NOW + 61)).toBeNull();
		expect(await verifyLaunchToken(token, "wrong", NOW)).toBeNull();
		expect(await verifyLaunchToken("garbage", SECRET, NOW)).toBeNull();
		expect(await verifyLaunchToken(null, SECRET, NOW)).toBeNull();
	});
});

describe("score envelopes", () => {
	it("accepts a well-formed envelope (node:crypto cross-check)", async () => {
		const store = createMemoryNonceStore();
		const result = await verifyEnvelope(await validEnvelope(), {
			serverSecret: SECRET,
			nonceStore: store,
			atSec: NOW,
		});
		expect(result).toEqual({ ok: true });
	});

	it("rejects tampered scores and wrong secrets", async () => {
		const store = createMemoryNonceStore();
		const tampered = await validEnvelope();
		tampered.score = 99999;
		expect(
			(
				await verifyEnvelope(tampered, {
					serverSecret: SECRET,
					nonceStore: store,
					atSec: NOW,
				})
			).reason,
		).toBe("bad-signature");

		const otherSecret = await validEnvelope();
		expect(
			(
				await verifyEnvelope(otherSecret, {
					serverSecret: "another-secret",
					nonceStore: createMemoryNonceStore(),
					atSec: NOW,
				})
			).reason,
		).toBe("bad-signature");
	});

	it("rejects replays and stale timestamps", async () => {
		const store = createMemoryNonceStore();
		const first = await validEnvelope({ nonce: "a".repeat(32) });
		expect(
			(
				await verifyEnvelope(first, {
					serverSecret: SECRET,
					nonceStore: store,
					atSec: NOW,
				})
			).ok,
		).toBe(true);
		const replay = { ...first };
		expect(
			(
				await verifyEnvelope(replay, {
					serverSecret: SECRET,
					nonceStore: store,
					atSec: NOW,
				})
			).reason,
		).toBe("replay");

		const stale = await validEnvelope({ timestamp: NOW - 500 });
		expect(
			(
				await verifyEnvelope(stale, {
					serverSecret: SECRET,
					nonceStore: createMemoryNonceStore(),
					atSec: NOW,
				})
			).reason,
		).toBe("stale");

		const future = await validEnvelope({ timestamp: NOW + 500 });
		expect(
			(
				await verifyEnvelope(future, {
					serverSecret: SECRET,
					nonceStore: createMemoryNonceStore(),
					atSec: NOW,
				})
			).reason,
		).toBe("stale");
	});

	it("rejects malformed envelopes", async () => {
		const store = createMemoryNonceStore();
		for (const bad of [
			{ ...(await validEnvelope()), score: -1 },
			{ ...(await validEnvelope()), score: 1.5 },
			{ ...(await validEnvelope()), durationSec: 0 },
			{ ...(await validEnvelope()), nonce: "short" },
			{ ...(await validEnvelope()), tag: "zz" },
			null,
		]) {
			expect(
				(
					await verifyEnvelope(bad, {
						serverSecret: SECRET,
						nonceStore: store,
						atSec: NOW,
					})
				).ok,
			).toBe(false);
		}
	});
});

describe("plausibility", () => {
	it("accepts credible runs and rejects absurd ones", () => {
		expect(checkPlausibility({ score: 250, durationSec: 42 })).toEqual({
			ok: true,
		});
		expect(
			checkPlausibility({ score: 250, durationSec: 42, chops: 250 }),
		).toEqual({
			ok: true,
		});
		expect(checkPlausibility({ score: 10000, durationSec: 5 }).reason).toBe(
			"inhuman-rate",
		);
		expect(checkPlausibility({ score: -3, durationSec: 5 }).reason).toBe(
			"bad-score",
		);
		expect(checkPlausibility({ score: 10, durationSec: 0 }).reason).toBe(
			"bad-duration",
		);
		expect(
			checkPlausibility({ score: 10, durationSec: 5, chops: 11 }).reason,
		).toBe("score-chops-mismatch");
	});
});

describe("misc", () => {
	it("builds the setGameScore call descriptor", () => {
		expect(
			buildSetGameScoreCall({ userId: 1, chatId: 2, messageId: 3, score: 250 }),
		).toEqual({
			method: "setGameScore",
			params: { user_id: 1, chat_id: 2, message_id: 3, score: 250 },
		});
		expect(
			buildSetGameScoreCall({ userId: 1, inlineMessageId: "AAQ", score: 250 }),
		).toEqual({
			method: "setGameScore",
			params: { user_id: 1, inline_message_id: "AAQ", score: 250 },
		});
	});

	it("compares in constant time on bytes only", () => {
		expect(
			timingSafeEqual(new Uint8Array([1, 2]), new Uint8Array([1, 2])),
		).toBe(true);
		expect(
			timingSafeEqual(new Uint8Array([1, 2]), new Uint8Array([1, 3])),
		).toBe(false);
		expect(timingSafeEqual(new Uint8Array([1]), new Uint8Array([1, 2]))).toBe(
			false,
		);
		expect(timingSafeEqual("ab", "ab")).toBe(false);
	});

	it("derives stable 32-byte session keys", async () => {
		const a = await deriveSessionKey(SECRET, "sid");
		const b = await deriveSessionKey(SECRET, "sid");
		const c = await deriveSessionKey(SECRET, "other");
		expect(a.length).toBe(32);
		expect(hex(a)).toBe(hex(b));
		expect(hex(a)).not.toBe(hex(c));
	});
});

describe("trace codec", () => {
	it("round-trips pack/deflate/inflate/unpack", async () => {
		const chops = [
			{ side: 0, t: 200 },
			{ side: 1, t: 450 },
			{ side: 0, t: 900 },
		];
		const raw = packTrace({ seedLo: 42, seedHi: 0, chops, endTimeMs: 1200 });
		expect(raw).not.toBeNull();
		const comp = await deflateTrace(raw);
		expect(comp.length).toBeLessThan(raw.length + 32);
		const back = unpackTrace(await inflateTrace(comp));
		expect(back).toEqual({ seedLo: 42, seedHi: 0, chops, endTimeMs: 1200 });
	});

	it("rejects malformed traces and payloads", async () => {
		expect(
			unpackTrace(
				new Uint8Array([9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]),
			),
		).toBeNull();
		expect(await inflateTrace(new Uint8Array([0, 1, 2, 3]))).toBeNull();
		expect(traceFromB64("!!!not-base64!!!")).toBeNull();
		expect(
			packTrace({
				seedLo: 1,
				seedHi: 0,
				chops: [{ side: 2, t: 5 }],
				endTimeMs: 9,
			}),
		).toBeNull();
		expect(
			packTrace({
				seedLo: 1,
				seedHi: 0,
				chops: [{ side: 0, t: 9 }],
				endTimeMs: 5,
			}),
		).not.toBeNull();
		// Time travel is caught at unpack.
		const bad = packTrace({
			seedLo: 1,
			seedHi: 0,
			chops: [
				{ side: 0, t: 9 },
				{ side: 1, t: 4 },
			],
			endTimeMs: 9,
		});
		expect(unpackTrace(bad)).toBeNull();
		const hash = await sha256Hex(new TextEncoder().encode("abc"));
		expect(hash).toBe(
			"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
		);
	});
});

describe("deterministic replay", () => {
	async function simWasm() {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		if (!existsSync("public/wasm/sim.wasm")) {
			return null;
		}
		return readFile("public/wasm/sim.wasm");
	}

	async function traceForSession(sides, stepMs) {
		const seedHex = await deriveSeed(SECRET, "sid-replay");
		// NB: Buffer.from pools memory — DataView must use byteOffset.
		const seedBytes = Buffer.from(seedHex, "hex");
		const view = new DataView(
			seedBytes.buffer,
			seedBytes.byteOffset,
			seedBytes.byteLength,
		);
		const chops = [];
		let t = 0;
		for (const side of sides) {
			t += stepMs;
			chops.push({ side, t });
		}
		const raw = packTrace({
			seedLo: view.getUint32(0, true),
			seedHi: view.getUint32(4, true),
			chops,
			endTimeMs: t,
		});
		const comp = await deflateTrace(raw);
		return Buffer.from(comp).toString("base64");
	}

	function alternating(n) {
		const sides = [];
		for (let i = 0; i < n; i++) {
			sides.push(i % 2 === 0 ? 0 : 1);
		}
		return sides;
	}

	it("accepts a trace whose replay matches the claim", async () => {
		const wasmBytes = await simWasm();
		if (!wasmBytes) {
			return;
		}
		// Pinned against the replay CLI for the derived seed of sid-replay:
		// score=2, branch death. Same artifact the server loads.
		const result = await replayTrace({
			traceB64: await traceForSession(alternating(60), 200),
			wasmBytes,
			claimed: { score: 2, alive: false, deathBranch: true },
			serverSecret: SECRET,
			sessionId: "sid-replay",
		});
		expect(result.ok).toBe(true);
		expect(result.replayed).toMatchObject({ score: 2, alive: false });
	});

	it("rejects inflated claims and garbage traces", async () => {
		const wasmBytes = await simWasm();
		if (!wasmBytes) {
			return;
		}
		const badClaim = await replayTrace({
			traceB64: await traceForSession(alternating(60), 200),
			wasmBytes,
			claimed: { score: 999, alive: false, deathBranch: true },
			serverSecret: SECRET,
			sessionId: "sid-replay",
		});
		expect(badClaim.ok).toBe(false);
		expect(badClaim.reason).toBe("no-outcome-match");

		const wrongSeed = await replayTrace({
			traceB64: await traceForSession(alternating(60), 200),
			wasmBytes,
			claimed: { score: 2, alive: false, deathBranch: true },
			serverSecret: SECRET,
			sessionId: "sid-other",
		});
		expect(wrongSeed.ok).toBe(false);
		expect(wrongSeed.reason).toBe("bad-seed");

		const garbage = await replayTrace({
			traceB64: Buffer.from([1, 2, 3]).toString("base64"),
			wasmBytes,
			claimed: { score: 0, alive: true, deathBranch: false },
		});
		expect(garbage.ok).toBe(false);
	});
});

describe("session registry", () => {
	it("keeps only the latest session and rate-limits issuance", () => {
		const reg = createSessionRegistry({ maxLaunchesPerHour: 2 });
		expect(reg.register(7, "s1", NOW)).toBe(true);
		expect(reg.isCurrent(7, "s1", NOW + 10)).toBe(true);
		expect(reg.register(7, "s2", NOW + 20)).toBe(true);
		expect(reg.isCurrent(7, "s1", NOW + 30)).toBe(false);
		expect(reg.isCurrent(7, "s2", NOW + 30)).toBe(true);
		expect(reg.register(7, "s3", NOW + 40)).toBe(false);
		expect(reg.isCurrent(9, "s9", NOW)).toBe(false);
	});
});
