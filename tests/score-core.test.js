import { createHmac, randomBytes } from "node:crypto";
import { describe, expect, it } from "vitest";
import {
	buildSetGameScoreCall,
	checkPlausibility,
	createMemoryNonceStore,
	deriveSessionKey,
	issueLaunchToken,
	timingSafeEqual,
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
	const base = {
		sessionId,
		score: 250,
		durationSec: 42,
		nonce: randomBytes(16).toString("hex"),
		timestamp: NOW,
		...overrides,
	};
	const key = await deriveSessionKey(SECRET, sessionId);
	const canonical = [
		"khanqah-v1",
		base.sessionId,
		String(base.score),
		String(base.durationSec),
		base.nonce,
		String(base.timestamp),
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
