import { createHmac, randomBytes } from "node:crypto";
import { describe, expect, it, vi } from "vitest";
import {
	canonicalEnvelope,
	loadSigner,
	SIGNER_WIRE_VERSION,
} from "../src/wasm/signer.ts";

// The loader must degrade gracefully: the game works with or without the
// compiled module. Crypto correctness is cross-checked against node:crypto
// (an independent implementation) plus the Rust RFC-vector unit tests.
describe("wasm signer loader", () => {
	it("returns null when the module is missing (404)", async () => {
		const fetchImpl = vi.fn(async () => new Response("nope", { status: 404 }));
		await expect(loadSigner(fetchImpl, "/")).resolves.toBeNull();
	});

	it("returns null when the bytes are not a module", async () => {
		const fetchImpl = vi.fn(
			async () =>
				new Response(new TextEncoder().encode("not-wasm"), { status: 200 }),
		);
		await expect(loadSigner(fetchImpl, "/")).resolves.toBeNull();
	});

	it("returns null when the exports do not match", async () => {
		const empty = new Uint8Array([
			0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
		]);
		const fetchImpl = vi.fn(async () => new Response(empty, { status: 200 }));
		await expect(loadSigner(fetchImpl, "/")).resolves.toBeNull();
	});

	it("loads the real module and matches node:crypto HMAC-SHA256", async () => {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		const path = "public/wasm/signer.wasm";
		if (!existsSync(path)) {
			return;
		}
		const bytes = await readFile(path);
		const fetchImpl = vi.fn(async () => new Response(bytes, { status: 200 }));
		const signer = await loadSigner(fetchImpl, "/");
		expect(signer?.version()).toBe(SIGNER_WIRE_VERSION);

		const key = randomBytes(32);
		expect(signer?.setSessionKey(key)).toBe(true);
		expect(signer?.setSessionKey(randomBytes(16))).toBe(false);

		const fields = {
			sessionId: "sid-test",
			score: 250,
			durationSec: 12,
			nonce: "0123456789abcdef0123456789abcdef",
			timestamp: 1700000000,
		};
		const expected = createHmac("sha256", key)
			.update(canonicalEnvelope(fields))
			.digest("hex");
		expect(signer?.signEnvelope(fields)).toBe(expected);
	});
});
