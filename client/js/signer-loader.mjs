/**
 * Loader for the Rust score-signer WASM module (wire v2).
 * Plain JavaScript for the legacy page (no TS pipeline): plain WebAssembly
 * instantiation, no glue deps. Returns null when the module is absent or
 * incompatible — the game must always work without it.
 *
 * Canonical envelope v2 (must match server/score-core.js exactly):
 *   `khanqah-v2\n${sessionId}\n${score}\n${durationSec}\n${nonce}\n${timestamp}\n${traceHash}`
 * as UTF-8 bytes, tagged with HMAC-SHA256 under the session key.
 *
 * @typedef {object} EnvelopeFields
 * @property {string} sessionId
 * @property {number} score
 * @property {number} durationSec
 * @property {string} nonce
 * @property {number} timestamp
 * @property {string} traceHash
 *
 * @typedef {object} ScoreSigner
 * @property {() => number} version
 * @property {(key: Uint8Array) => boolean} setSessionKey
 * @property {(message: Uint8Array) => Uint8Array | null} signBytes
 * @property {(fields: EnvelopeFields) => string | null} signEnvelope
 */

export const SIGNER_WIRE_VERSION = 2;

export function canonicalEnvelope(fields) {
	const text = [
		"khanqah-v2",
		fields.sessionId,
		String(fields.score),
		String(fields.durationSec),
		fields.nonce,
		String(fields.timestamp),
		fields.traceHash,
	].join("\n");
	return new TextEncoder().encode(text);
}

function toHex(bytes) {
	return Array.from(bytes)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

function wrap(exports) {
	const raw = exports;
	const need = [
		"signer_version",
		"max_msg_len",
		"init_session",
		"msg_buffer_ptr",
		"tag_buffer_ptr",
		"sign_tag",
		"memory",
	];
	if (
		typeof raw.signer_version !== "function" ||
		raw.signer_version() !== SIGNER_WIRE_VERSION ||
		need.some((k) => raw[k] === undefined)
	) {
		return null;
	}
	const memory = raw.memory;
	const maxLen = raw.max_msg_len();
	const initSession = raw.init_session;
	const msgPtr = raw.msg_buffer_ptr;
	const tagPtr = raw.tag_buffer_ptr;
	const signTag = raw.sign_tag;

	function setSessionKey(key) {
		if (!(key instanceof Uint8Array) || key.length !== 32) {
			return false;
		}
		try {
			const slot = new Uint8Array(memory.buffer, msgPtr(), key.length);
			slot.set(key);
			return initSession(msgPtr(), key.length) === 0;
		} catch {
			return false;
		}
	}

	function signBytes(message) {
		if (
			!(message instanceof Uint8Array) ||
			message.length === 0 ||
			message.length > maxLen
		) {
			return null;
		}
		try {
			new Uint8Array(memory.buffer, msgPtr(), message.length).set(message);
			if (signTag(message.length) !== 0) {
				return null;
			}
			return new Uint8Array(memory.buffer.slice(tagPtr(), tagPtr() + 32));
		} catch {
			return null;
		}
	}

	return {
		version: () => raw.signer_version(),
		setSessionKey,
		signBytes,
		signEnvelope: (fields) => {
			const tag = signBytes(canonicalEnvelope(fields));
			return tag ? toHex(tag) : null;
		},
	};
}

// fetchImpl defaults to a bound closure: a detached bare `fetch`
// reference throws Illegal invocation on some browsers.
export async function loadSigner(
	fetchImpl = (...args) => fetch(...args),
	base = "/",
) {
	try {
		const response = await fetchImpl(`${base}wasm/signer.wasm`);
		if (!response.ok) {
			return null;
		}
		const bytes = await response.arrayBuffer();
		const { instance } = await WebAssembly.instantiate(bytes);
		return wrap(instance.exports);
	} catch {
		return null;
	}
}
