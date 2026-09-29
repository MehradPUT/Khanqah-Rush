/**
 * Minimal loader for the Rust score-signer WASM stub.
 * Plain WebAssembly instantiation, no glue deps. Returns null when the
 * module is absent or incompatible — the game must always work without it
 * until the signed-score task makes signing real.
 */

export const SIGNER_WIRE_VERSION = 1;

export interface ScoreSigner {
	version(): number;
	signScoreStub(score: number): number;
}

interface RawSignerExports {
	signer_version: () => number;
	sign_score_stub: (score: number) => number;
}

function wrap(exports: WebAssembly.Exports): ScoreSigner | null {
	const raw = exports as unknown as Partial<RawSignerExports>;
	const versionFn = raw.signer_version;
	const signFn = raw.sign_score_stub;
	if (typeof versionFn !== "function" || typeof signFn !== "function") {
		return null;
	}
	if (versionFn() !== SIGNER_WIRE_VERSION) {
		return null;
	}
	return {
		version: () => versionFn(),
		signScoreStub: (score: number) => signFn(score),
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
