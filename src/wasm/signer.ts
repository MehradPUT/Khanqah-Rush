/**
 * Loader for the Rust score-signer WASM module (wire v2).
 * Plain WebAssembly instantiation, no glue deps. Returns null when the
 * module is absent or incompatible — the game must always work without it.
 *
 * Canonical envelope (must match server/score-core.js exactly):
 *   `khanqah-v1\n${sessionId}\n${score}\n${durationSec}\n${nonce}\n${timestamp}`
 * as UTF-8 bytes, tagged with HMAC-SHA256 under the session key.
 */

export const SIGNER_WIRE_VERSION = 2;

export interface EnvelopeFields {
	sessionId: string;
	score: number;
	durationSec: number;
	nonce: string;
	timestamp: number;
}

export interface ScoreSigner {
	version(): number;
	setSessionKey(key: Uint8Array): boolean;
	signBytes(message: Uint8Array): Uint8Array | null;
	signEnvelope(fields: EnvelopeFields): string | null;
}

interface RawSignerExports {
	signer_version: () => number;
	max_msg_len: () => number;
	init_session: (ptr: number, len: number) => number;
	msg_buffer_ptr: () => number;
	tag_buffer_ptr: () => number;
	sign_tag: (len: number) => number;
	memory: WebAssembly.Memory;
}

export function canonicalEnvelope(fields: EnvelopeFields): Uint8Array {
	const text = [
		"khanqah-v1",
		fields.sessionId,
		String(fields.score),
		String(fields.durationSec),
		fields.nonce,
		String(fields.timestamp),
	].join("\n");
	return new TextEncoder().encode(text);
}

function toHex(bytes: Uint8Array): string {
	return Array.from(bytes)
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

function wrap(exports: WebAssembly.Exports): ScoreSigner | null {
	const raw = exports as unknown as Partial<RawSignerExports>;
	const need: (keyof RawSignerExports)[] = [
		"signer_version",
		"max_msg_len",
		"init_session",
		"msg_buffer_ptr",
		"tag_buffer_ptr",
		"sign_tag",
		"memory",
	];
	if (
		raw.signer_version?.() !== SIGNER_WIRE_VERSION ||
		need.some((k) => raw[k] === undefined)
	) {
		return null;
	}
	const memory = raw.memory as WebAssembly.Memory;
	const maxLen = (raw.max_msg_len as () => number)();
	const initSession = raw.init_session as (ptr: number, len: number) => number;
	const msgPtr = raw.msg_buffer_ptr as () => number;
	const tagPtr = raw.tag_buffer_ptr as () => number;
	const signTag = raw.sign_tag as (len: number) => number;

	function setSessionKey(key: Uint8Array): boolean {
		if (key.length !== 32) {
			return false;
		}
		const slot = new Uint8Array(memory.buffer, msgPtr(), key.length);
		slot.set(key);
		return initSession(msgPtr(), key.length) === 0;
	}

	function signBytes(message: Uint8Array): Uint8Array | null {
		if (message.length === 0 || message.length > maxLen) {
			return null;
		}
		new Uint8Array(memory.buffer, msgPtr(), message.length).set(message);
		if (signTag(message.length) !== 0) {
			return null;
		}
		return new Uint8Array(memory.buffer.slice(tagPtr(), tagPtr() + 32));
	}

	return {
		version: () => (raw.signer_version as () => number)(),
		setSessionKey,
		signBytes,
		signEnvelope: (fields: EnvelopeFields) => {
			const tag = signBytes(canonicalEnvelope(fields));
			return tag ? toHex(tag) : null;
		},
	};
}

export async function loadSigner(
	fetchImpl: typeof fetch = fetch,
	base: string = import.meta.env.BASE_URL,
): Promise<ScoreSigner | null> {
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
