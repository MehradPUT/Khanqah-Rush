/**
 * Framework-free score-verification core for Khanqah Rush.
 *
 * Pure functions over WebCrypto (globalThis.crypto.subtle), so the same
 * module runs on Node 18+ and Cloudflare Workers with no dependencies.
 * Transport adapters (node:http example, future Worker entry) live outside.
 *
 * Canonical envelope — must match src/wasm/signer.ts exactly:
 *   `khanqah-v1\n${sessionId}\n${score}\n${durationSec}\n${nonce}\n${timestamp}`
 */

export const ENVELOPE_VERSION = "khanqah-v1";
export const TIMESTAMP_WINDOW_SEC = 60;
export const NONCE_TTL_SEC = 180;
export const MAX_CPS = 10;

const textEncoder = new TextEncoder();
const textDecoder = new TextDecoder();

function toBytes(str) {
	return textEncoder.encode(str);
}

function fromHex(hex) {
	if (
		typeof hex !== "string" ||
		hex.length % 2 !== 0 ||
		!/^[0-9a-f]*$/.test(hex)
	) {
		return null;
	}
	const out = new Uint8Array(hex.length / 2);
	for (let i = 0; i < out.length; i++) {
		out[i] = Number.parseInt(hex.slice(i * 2, i * 2 + 2), 16);
	}
	return out;
}

function b64urlEncode(bytes) {
	let bin = "";
	for (const b of bytes) {
		bin += String.fromCharCode(b);
	}
	return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function b64urlDecode(str) {
	try {
		const b64 = str.replace(/-/g, "+").replace(/_/g, "/");
		const bin = atob(b64);
		const out = new Uint8Array(bin.length);
		for (let i = 0; i < bin.length; i++) {
			out[i] = bin.charCodeAt(i);
		}
		return out;
	} catch {
		return null;
	}
}

async function hmacSha256(keyBytes, msgBytes) {
	const key = await crypto.subtle.importKey(
		"raw",
		keyBytes,
		{ name: "HMAC", hash: "SHA-256" },
		false,
		["sign"],
	);
	const sig = await crypto.subtle.sign("HMAC", key, msgBytes);
	return new Uint8Array(sig);
}

/** Constant-time equality. Length mismatch fails without early content exit. */
export function timingSafeEqual(a, b) {
	if (!(a instanceof Uint8Array) || !(b instanceof Uint8Array)) {
		return false;
	}
	if (a.length !== b.length) {
		return false;
	}
	let diff = 0;
	for (let i = 0; i < a.length; i++) {
		diff |= a[i] ^ b[i];
	}
	return diff === 0;
}

function nowSec() {
	return Math.floor(Date.now() / 1000);
}

/**
 * Issue a launch token for a game start. Embed in the answered game URL;
 * the client echoes it back with every score post. Regular launches carry
 * user/chat/message ids; inline launches carry the inline message id
 * instead (there is no chat message to bind to).
 */
export async function issueLaunchToken(
	{ userId, chatId, messageId, inlineMessageId, ttlSec = 3600 },
	serverSecret,
	atSec = nowSec(),
) {
	const payload = {
		u: userId,
		exp: atSec + ttlSec,
	};
	if (typeof inlineMessageId === "string" && inlineMessageId.length > 0) {
		payload.i = inlineMessageId;
	} else {
		payload.c = chatId;
		payload.m = messageId;
	}
	const body = b64urlEncode(toBytes(JSON.stringify(payload)));
	const sig = await hmacSha256(toBytes(serverSecret), toBytes(body));
	return `${body}.${b64urlEncode(sig)}`;
}

/** Verify a launch token. Returns the payload or null. */
export async function verifyLaunchToken(token, serverSecret, atSec = nowSec()) {
	if (typeof token !== "string") {
		return null;
	}
	const dot = token.lastIndexOf(".");
	if (dot === -1) {
		return null;
	}
	const body = token.slice(0, dot);
	const sig = b64urlDecode(token.slice(dot + 1));
	if (!sig) {
		return null;
	}
	const expected = await hmacSha256(toBytes(serverSecret), toBytes(body));
	if (!timingSafeEqual(sig, expected)) {
		return null;
	}
	let payload;
	try {
		payload = JSON.parse(
			textDecoder.decode(b64urlDecode(body) ?? new Uint8Array()),
		);
	} catch {
		return null;
	}
	if (
		!payload ||
		typeof payload.exp !== "number" ||
		payload.exp < atSec ||
		!Number.isInteger(payload.u) ||
		!(
			(typeof payload.i === "string" && payload.i.length > 0) ||
			(Number.isInteger(payload.c) && Number.isInteger(payload.m))
		)
	) {
		return null;
	}
	return payload;
}

/** Derive a 32-byte per-session signing key. Client receives it at launch. */
export async function deriveSessionKey(serverSecret, sessionId) {
	return hmacSha256(
		toBytes(serverSecret),
		toBytes(`khanqah-session\n${sessionId}`),
	);
}

export function canonicalEnvelope({
	sessionId,
	score,
	durationSec,
	nonce,
	timestamp,
}) {
	return toBytes(
		[
			ENVELOPE_VERSION,
			sessionId,
			String(score),
			String(durationSec),
			nonce,
			String(timestamp),
		].join("\n"),
	);
}

/** In-memory nonce store with TTL sweep. Single isolate only — see docs. */
export function createMemoryNonceStore() {
	const seen = new Map();
	return {
		checkAndAdd(nonce, ttlSec = NONCE_TTL_SEC, atSec = nowSec()) {
			for (const [key, expires] of seen) {
				if (expires <= atSec) {
					seen.delete(key);
				}
			}
			if (seen.has(nonce)) {
				return false;
			}
			seen.set(nonce, atSec + ttlSec);
			return true;
		},
	};
}

/**
 * Verify a score envelope. Returns { ok: true } or { ok: false, reason }.
 * Reasons: bad-shape | stale | replay | bad-signature. Reasons stay
 * server-side — the transport must answer 200 either way.
 */
export async function verifyEnvelope(
	envelope,
	{
		serverSecret,
		nonceStore,
		windowSec = TIMESTAMP_WINDOW_SEC,
		atSec = nowSec(),
	},
) {
	const { sessionId, score, durationSec, nonce, timestamp, tag } =
		envelope ?? {};
	if (
		typeof sessionId !== "string" ||
		sessionId.length === 0 ||
		!Number.isInteger(score) ||
		score < 0 ||
		typeof durationSec !== "number" ||
		!(durationSec > 0) ||
		typeof nonce !== "string" ||
		!/^[0-9a-f]{32}$/.test(nonce) ||
		!Number.isInteger(timestamp) ||
		typeof tag !== "string"
	) {
		return { ok: false, reason: "bad-shape" };
	}
	if (Math.abs(atSec - timestamp) > windowSec) {
		return { ok: false, reason: "stale" };
	}
	if (!nonceStore.checkAndAdd(nonce)) {
		return { ok: false, reason: "replay" };
	}
	const sessionKey = await deriveSessionKey(serverSecret, sessionId);
	const expected = await hmacSha256(
		sessionKey,
		canonicalEnvelope({ sessionId, score, durationSec, nonce, timestamp }),
	);
	const got = fromHex(tag);
	if (!got || !timingSafeEqual(got, expected)) {
		return { ok: false, reason: "bad-signature" };
	}
	return { ok: true };
}

/**
 * Physics plausibility for lumberjack scoring. Returns { ok, reason }.
 * Generous on purpose — this layer catches absurd fabrications, while
 * subtle cheating goes to the anomaly queue, not to hard rejection.
 */
export function checkPlausibility({ score, durationSec, chops }) {
	if (!Number.isInteger(score) || score < 0) {
		return { ok: false, reason: "bad-score" };
	}
	if (typeof durationSec !== "number" || !(durationSec > 0)) {
		return { ok: false, reason: "bad-duration" };
	}
	if (score > Math.ceil(durationSec * MAX_CPS)) {
		return { ok: false, reason: "inhuman-rate" };
	}
	if (chops !== undefined && chops !== score) {
		return { ok: false, reason: "score-chops-mismatch" };
	}
	return { ok: true };
}

/** Transport-agnostic Bot API call descriptor for setGameScore. */
export function buildSetGameScoreCall({
	userId,
	chatId,
	messageId,
	inlineMessageId,
	score,
}) {
	if (typeof inlineMessageId === "string") {
		return {
			method: "setGameScore",
			params: { user_id: userId, inline_message_id: inlineMessageId, score },
		};
	}
	return {
		method: "setGameScore",
		params: { user_id: userId, chat_id: chatId, message_id: messageId, score },
	};
}
