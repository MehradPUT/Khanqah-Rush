/**
 * Framework-free score-verification core for Khanqah Rush.
 *
 * Pure functions over WebCrypto (globalThis.crypto.subtle), so the same
 * module runs on Node 18+ and Cloudflare Workers with no dependencies.
 * Transport adapters (node:http example, future Worker entry) live outside.
 *
 * Canonical envelope v2 — must match client/js/signer-loader.mjs exactly:
 *   `khanqah-v2\n${sessionId}\n${score}\n${durationSec}\n${nonce}\n${timestamp}\n${traceHash}`
 * traceHash binds the (possibly absent during transition) trace.
 */

export const ENVELOPE_VERSION = "khanqah-v2";
export const TIMESTAMP_WINDOW_SEC = 60;
export const NONCE_TTL_SEC = 180;
export const MAX_CPS = 10;
// Session lifetime after mint, enforced statelessly from the launch
// token's `sat` claim (no server memory: Workers isolates don't share
// any, so an in-memory "current session" check fails across isolates).
export const SESSION_TTL_SEC = 3600;

const textEncoder = new TextEncoder();
const textDecoder = new TextDecoder();

function toBytes(str) {
	return textEncoder.encode(str);
}

function toHex(bytes) {
	return Array.from(bytes)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
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
 *
 * The session id rides inside the signed payload (`s`, minted at `sat`)
 * so score posts validate statelessly — no shared store needed across
 * isolates. sessionId is required; old tokens without it verify as null.
 */
export async function issueLaunchToken(
	{ userId, chatId, messageId, inlineMessageId, sessionId, ttlSec = 3600 },
	serverSecret,
	atSec = nowSec(),
) {
	if (typeof sessionId !== "string" || sessionId.length === 0) {
		throw new Error("sessionId is required");
	}
	const payload = {
		u: userId,
		exp: atSec + ttlSec,
		s: sessionId,
		sat: atSec,
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
		typeof payload.s !== "string" ||
		payload.s.length === 0 ||
		!Number.isInteger(payload.sat) ||
		!(
			(typeof payload.i === "string" && payload.i.length > 0) ||
			(Number.isInteger(payload.c) && Number.isInteger(payload.m))
		)
	) {
		return null;
	}
	return payload;
}

/**
 * Stateless session check: the posted sid must be the token-bound one
 * and the session must be younger than SESSION_TTL_SEC. Pure function —
 * safe to call on any isolate.
 */
export function isSessionLive(launch, sessionId, atSec = nowSec()) {
	return (
		!!launch &&
		launch.s === sessionId &&
		Number.isInteger(launch.sat) &&
		atSec - launch.sat < SESSION_TTL_SEC
	);
}

/** Derive a 32-byte per-session signing key. Client receives it at launch. */
export async function deriveSessionKey(serverSecret, sessionId) {
	return hmacSha256(
		toBytes(serverSecret),
		toBytes(`khanqah-session\n${sessionId}`),
	);
}

/**
 * Derive the per-session sim seed (hex16) bound to the session id.
 * Deterministic — the server recomputes it instead of storing it.
 * Minted into the answered game URL next to sid/sk.
 */
export async function deriveSeed(serverSecret, sessionId) {
	const full = await hmacSha256(
		toBytes(serverSecret),
		toBytes(`khanqah-seed\n${sessionId}`),
	);
	return toHex(full.slice(0, 8));
}

export function canonicalEnvelope({
	sessionId,
	score,
	durationSec,
	nonce,
	timestamp,
	traceHash,
}) {
	return toBytes(
		[
			ENVELOPE_VERSION,
			sessionId,
			String(score),
			String(durationSec),
			nonce,
			String(timestamp),
			traceHash,
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
 * Reasons: bad-shape | stale | replay | bad-signature | bad-trace.
 * Reasons stay server-side — the transport must answer 200 either way.
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
	const {
		sessionId,
		score,
		durationSec,
		nonce,
		timestamp,
		tag,
		trace,
		traceHash,
	} = envelope ?? {};
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
		typeof tag !== "string" ||
		typeof trace !== "string" ||
		typeof traceHash !== "string" ||
		!/^[0-9a-f]{64}$/.test(traceHash)
	) {
		return { ok: false, reason: "bad-shape" };
	}
	if (Math.abs(atSec - timestamp) > windowSec) {
		return { ok: false, reason: "stale" };
	}
	if (!nonceStore.checkAndAdd(nonce)) {
		return { ok: false, reason: "replay" };
	}
	const traceBytes = traceFromB64(trace);
	if (!traceBytes || traceBytes.length > TRACE_MAX_BYTES) {
		return { ok: false, reason: "bad-trace" };
	}
	const actualHash = toHex(
		new Uint8Array(await crypto.subtle.digest("SHA-256", traceBytes)),
	);
	if (actualHash !== traceHash.toLowerCase()) {
		return { ok: false, reason: "bad-trace" };
	}
	const sessionKey = await deriveSessionKey(serverSecret, sessionId);
	const expected = await hmacSha256(
		sessionKey,
		canonicalEnvelope({
			sessionId,
			score,
			durationSec,
			nonce,
			timestamp,
			traceHash,
		}),
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

// ---------------------------------------------------------------------------
// Trace codec lives in shared/trace-codec.js (single source for page,
// server, and tests). Imported for internal use and re-exported so
// existing importers keep working.
// ---------------------------------------------------------------------------
import {
	packTrace,
	sha256Hex,
	splitSeedHex,
	TRACE_MAX_BYTES,
	TRACE_MAX_CHOPS,
	TRACE_VERSION,
	traceFromB64,
	traceToB64,
	unpackTrace,
} from "../shared/trace-codec.js";

export {
	packTrace,
	sha256Hex,
	splitSeedHex,
	TRACE_MAX_BYTES,
	TRACE_MAX_CHOPS,
	TRACE_VERSION,
	traceFromB64,
	traceToB64,
	unpackTrace,
};

/**
 * Replay a trace through the deterministic sim and compare with the claim.
 * The seed is re-derived from (serverSecret, sessionId) and must match the
 * trace-embedded seed — clients cannot shop for favorable seeds.
 * wasmBytes: Uint8Array of the sim.wasm module bytes (caller reads from
 * disk on node, self-fetches on Workers; the compiled module is cached by
 * the caller if replays are frequent).
 * Returns { ok: true, replayed } or { ok: false, reason }.
 * Reasons: bad-trace | bad-seed | no-outcome-match.
 */
export async function replayTrace({
	traceB64,
	wasmBytes,
	claimed,
	serverSecret,
	sessionId,
}) {
	const raw = typeof traceB64 === "string" ? traceFromB64(traceB64) : null;
	if (!raw || raw.length > TRACE_MAX_BYTES) {
		return { ok: false, reason: "bad-trace" };
	}
	const trace = unpackTrace(raw);
	if (!trace) {
		return { ok: false, reason: "bad-trace" };
	}
	const seedHex = await deriveSeed(serverSecret, sessionId);
	const seedBytes = fromHex(seedHex);
	const seedView = new DataView(seedBytes.buffer);
	if (
		seedView.getUint32(0, true) !== trace.seedLo >>> 0 ||
		seedView.getUint32(4, true) !== trace.seedHi >>> 0
	) {
		return { ok: false, reason: "bad-seed" };
	}
	let instance;
	try {
		({ instance } = await WebAssembly.instantiate(wasmBytes));
	} catch {
		return { ok: false, reason: "bad-trace" };
	}
	const sim = instance.exports;
	if (typeof sim.sim_version !== "function" || sim.sim_version() !== 2) {
		return { ok: false, reason: "bad-trace" };
	}
	const seed = (BigInt(trace.seedHi >>> 0) << 32n) | BigInt(trace.seedLo >>> 0);
	sim.sim_reset(Number(seed & 0xffffffffn), Number(seed >> 32n));
	// Trace v1 carries no hero id; pin Nima explicitly (also the sim's
	// default). Non-Nima rounds replay-mismatch by design until trace v2.
	if (typeof sim.sim_set_character === "function") {
		sim.sim_set_character(0);
	}
	for (const chop of trace.chops) {
		// sim sides: 1 = LEFT, 2 = RIGHT; trace sides: 0 = LEFT, 1 = RIGHT.
		const ev = sim.sim_chop(chop.side === 0 ? 1 : 2, chop.t);
		if (ev !== 0) {
			break;
		}
	}
	sim.sim_advance_idle(trace.endTimeMs);
	const replayed = {
		score: sim.sim_score(),
		alive: sim.sim_alive() === 1,
		deathBranch: sim.sim_death_reason() === 1,
		survivalMs: Number(sim.sim_survival_ms()),
	};
	const match =
		replayed.score === claimed.score && replayed.alive === claimed.alive;
	if (!match) {
		return { ok: false, reason: "no-outcome-match", replayed };
	}
	return { ok: true, replayed };
}

/**
 * Issuance rate limiter (launches per user per hour). Best-effort and
 * per-isolate by nature — it only decides whether a Play press gets a
 * session URL, never whether a score records. Session validity itself
 * is stateless (see isSessionLive), so scoring works on any isolate.
 * No single-active-session eviction: every minted session stays valid
 * for SESSION_TTL_SEC. Parallel seed-shopping costs a fully played round
 * per seed while replay still binds each score to real inputs, so the
 * residual is accepted.
 */
export function createSessionRegistry({ maxLaunchesPerHour = 30 } = {}) {
	// userId -> { launches: [atSec...] }
	const users = new Map();
	return {
		register(userId, atSec = nowSec()) {
			let entry = users.get(userId);
			if (!entry) {
				entry = { launches: [] };
				users.set(userId, entry);
			}
			entry.launches = entry.launches.filter((t) => t > atSec - 3600);
			if (entry.launches.length >= maxLaunchesPerHour) {
				return false;
			}
			entry.launches.push(atSec);
			return true;
		},
	};
}
