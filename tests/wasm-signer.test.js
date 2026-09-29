import { describe, expect, it, vi } from "vitest";
import { loadSigner } from "../src/wasm/signer.ts";

// The stub-phase loader must degrade gracefully: the game works with or
// without the compiled module. Real sign/verify coverage lands with the
// signed-score task.
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

	it("loads the real stub when built (round-trips version and stub call)", async () => {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		const path = "public/wasm/signer.wasm";
		if (!existsSync(path)) {
			return;
		}
		const bytes = await readFile(path);
		const fetchImpl = vi.fn(async () => new Response(bytes, { status: 200 }));
		const signer = await loadSigner(fetchImpl, "/");
		expect(signer?.version()).toBe(1);
		expect(signer?.signScoreStub(100)).toBe(100 ^ 0x5a5a5a5a);
	});
});
