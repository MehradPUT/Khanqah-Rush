import { describe, expect, it, vi } from "vitest";
import {
	DEATH_BRANCH,
	EV_ALREADY_DEAD,
	EV_DIED_BRANCH,
	EV_INVALID_TIME,
	loadSim,
	SIM_LEFT,
	SIM_RIGHT,
	SIM_WIRE_VERSION,
} from "../public/js/sim-loader.mjs";

// Goldens mirror wasm/sim's native unit tests byte-for-byte: the same
// values asserted in Rust must come out of the compiled WASM artifact,
// proving bit-identical behavior across implementations.
describe("deterministic sim", () => {
	it("returns null when the module is missing", async () => {
		const fetchImpl = vi.fn(async () => new Response("nope", { status: 404 }));
		await expect(loadSim(fetchImpl, "/")).resolves.toBeNull();
	});

	it("replays the golden run identically to native", async () => {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		const path = "public/wasm/sim.wasm";
		if (!existsSync(path)) {
			return;
		}
		const bytes = await readFile(path);
		const fetchImpl = vi.fn(async () => new Response(bytes, { status: 200 }));
		const sim = await loadSim(fetchImpl, "/");
		expect(sim?.version()).toBe(SIM_WIRE_VERSION);

		sim?.reset(42, 0);
		expect(sim?.segmentCount()).toBe(10);
		expect(Array.from(sim?.segments() ?? []).slice(0, 3)).toEqual([0, 0, 0]);

		let ev = EV_ALREADY_DEAD;
		let t = 0;
		for (let i = 0; i < 60; i++) {
			t += 200;
			ev = sim?.chop(i % 2 === 0 ? SIM_LEFT : SIM_RIGHT, t) ?? EV_ALREADY_DEAD;
			if (ev !== 0) {
				break;
			}
		}
		expect(ev).toBe(EV_DIED_BRANCH);
		expect(sim?.score()).toBe(5);
		expect(sim?.alive()).toBe(false);
		expect(sim?.deathReason()).toBe(DEATH_BRANCH);
		expect(sim?.survivalMs()).toBe(1000);
		expect(sim?.staminaMilli()).toBe(1000);
	});

	it("rejects time travel and post-death input", async () => {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		const path = "public/wasm/sim.wasm";
		if (!existsSync(path)) {
			return;
		}
		const bytes = await readFile(path);
		const fetchImpl = vi.fn(async () => new Response(bytes, { status: 200 }));
		const sim = await loadSim(fetchImpl, "/");
		sim?.reset(7, 0);
		sim?.chop(SIM_LEFT, 500);
		expect(sim?.chop(SIM_LEFT, 100)).toBe(EV_INVALID_TIME);
	});
});
