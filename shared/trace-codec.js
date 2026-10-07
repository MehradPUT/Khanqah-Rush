/**
 * Trace codec shared by the page companion, the server core, and tests.
 * Single source — no copies. Runs on Node 18+, browsers, and Workers
 * (only Web-standard APIs: atob/btoa, subtle crypto).
 *
 * Traces ship RAW (no compression): typical rounds are under 100 bytes
 * and even the 10k-chop cap fits a POST easily. CompressionStream is
 * deliberately avoided — several mobile browsers never resolve it.
 *
 * Trace v1 binary layout (all integers little-endian):
 *   u8 version (1) || u32 seed_lo || u32 seed_hi || u16 chop count ||
 *   entries || u32 end_t_ms. Each entry is u32 t_ms + u8 side (0 LEFT,
 *   1 RIGHT). Transported base64-encoded.
 */

export const TRACE_VERSION = 1;
export const TRACE_MAX_BYTES = 65536;
export const TRACE_MAX_CHOPS = 10000;

export function packTrace({ seedLo, seedHi, chops, endTimeMs }) {
	if (
		!Number.isInteger(seedLo) ||
		!Number.isInteger(seedHi) ||
		!Array.isArray(chops) ||
		chops.length > TRACE_MAX_CHOPS ||
		!Number.isInteger(endTimeMs)
	) {
		return null;
	}
	const raw = new Uint8Array(1 + 4 + 4 + 2 + chops.length * 5 + 4);
	const view = new DataView(raw.buffer);
	let o = 0;
	view.setUint8(o, TRACE_VERSION);
	o += 1;
	view.setUint32(o, seedLo >>> 0, true);
	o += 4;
	view.setUint32(o, seedHi >>> 0, true);
	o += 4;
	view.setUint16(o, chops.length, true);
	o += 2;
	for (const chop of chops) {
		if (
			!chop ||
			!Number.isInteger(chop.t) ||
			chop.t < 0 ||
			(chop.side !== 0 && chop.side !== 1)
		) {
			return null;
		}
		view.setUint32(o, chop.t >>> 0, true);
		o += 4;
		view.setUint8(o, chop.side);
		o += 1;
	}
	view.setUint32(o, endTimeMs >>> 0, true);
	return raw;
}

export function unpackTrace(raw) {
	if (!(raw instanceof Uint8Array) || raw.length < 15) {
		return null;
	}
	const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
	let o = 0;
	if (view.getUint8(o) !== TRACE_VERSION) {
		return null;
	}
	o += 1;
	const seedLo = view.getUint32(o, true);
	o += 4;
	const seedHi = view.getUint32(o, true);
	o += 4;
	const count = view.getUint16(o, true);
	o += 2;
	if (count > TRACE_MAX_CHOPS || raw.length !== 1 + 4 + 4 + 2 + count * 5 + 4) {
		return null;
	}
	const chops = [];
	let prevT = 0;
	for (let i = 0; i < count; i++) {
		const t = view.getUint32(o, true);
		o += 4;
		const side = view.getUint8(o);
		o += 1;
		if ((side !== 0 && side !== 1) || t < prevT) {
			return null;
		}
		prevT = t;
		chops.push({ side, t });
	}
	const endTimeMs = view.getUint32(o, true);
	if (endTimeMs < prevT) {
		return null;
	}
	return { seedLo, seedHi, chops, endTimeMs };
}

function b64Encode(bytes) {
	let bin = "";
	const CHUNK = 8192;
	for (let i = 0; i < bytes.length; i += CHUNK) {
		bin += String.fromCharCode(...bytes.subarray(i, i + CHUNK));
	}
	return btoa(bin);
}

function b64Decode(str) {
	try {
		const bin = atob(str);
		const out = new Uint8Array(bin.length);
		for (let i = 0; i < bin.length; i++) {
			out[i] = bin.charCodeAt(i);
		}
		return out;
	} catch {
		return null;
	}
}

export function traceToB64(raw) {
	return b64Encode(raw);
}

export function traceFromB64(str) {
	if (typeof str !== "string" || str.length === 0) {
		return null;
	}
	return b64Decode(str);
}

/** Hex SHA-256 over bytes (WebCrypto; works on node, browsers, Workers). */
export async function sha256Hex(bytes) {
	const digest = await crypto.subtle.digest("SHA-256", bytes);
	return Array.from(new Uint8Array(digest))
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

/** Split a 16-hex-char seed into LE u32 halves (matches replayTrace). */ export function splitSeedHex(
	hex16,
) {
	if (typeof hex16 !== "string" || !/^[0-9a-f]{16}$/.test(hex16)) {
		return null;
	}
	const bytes = new Uint8Array(8);
	for (let i = 0; i < 8; i++) {
		bytes[i] = Number.parseInt(hex16.slice(i * 2, i * 2 + 2), 16);
	}
	const view = new DataView(bytes.buffer);
	return {
		seedLo: view.getUint32(0, true) >>> 0,
		seedHi: view.getUint32(4, true) >>> 0,
	};
}
