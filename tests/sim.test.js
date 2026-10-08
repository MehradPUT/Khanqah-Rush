import { describe, expect, it, vi } from "vitest";
import {
	DEATH_BRANCH,
	EV_ALREADY_DEAD,
	EV_DIED_BRANCH,
	EV_DIED_EXHAUSTION,
	EV_INVALID_TIME,
	loadSim,
	SIM_LEFT,
	SIM_RIGHT,
	SIM_WIRE_VERSION,
} from "../client/js/sim-loader.mjs";

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
		expect(sim?.segmentCount()).toBe(12);
		expect(Array.from(sim?.segments() ?? []).slice(0, 2)).toEqual([0, 0]);

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
		expect(sim?.score()).toBe(3);
		expect(sim?.alive()).toBe(false);
		expect(sim?.deathReason()).toBe(DEATH_BRANCH);
		expect(sim?.survivalMs()).toBe(800);
		expect(sim?.staminaMilli()).toBe(0);
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

	it("pins stamina through Nima's rejuvenation window", async () => {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		const path = "public/wasm/sim.wasm";
		if (!existsSync(path)) {
			return;
		}
		const bytes = await readFile(path);
		const fetchImpl = vi.fn(async () => new Response(bytes, { status: 200 }));
		const sim = await loadSim(fetchImpl, "/");
		if (!sim) {
			return;
		}
		// Safe-side play into the first 15 s window, then idle past the
		// plain deadline: Nima lives, ability-free Fateme dies.
		const playToWindow = () => {
			let t = 0;
			let ev = EV_ALREADY_DEAD;
			for (let i = 0; i < 100; i++) {
				t += 150;
				const bottom = (sim.segments() ?? [])[0] ?? 0;
				ev = sim.chop(bottom < 0 ? SIM_RIGHT : SIM_LEFT, t);
				if (ev !== 0) {
					break;
				}
			}
			return { t, ev };
		};
		sim.reset(42, 0);
		expect(playToWindow()).toMatchObject({ t: 15000, ev: 0 });
		expect(sim.rejuvenations()).toBe(1);
		expect(sim.advanceIdle(24000)).toBe(0);
		expect(sim.alive()).toBe(true);

		if (typeof sim.setCharacter === "function") {
			sim.reset(42, 0);
			sim.setCharacter(7);
			expect(playToWindow()).toMatchObject({ t: 15000, ev: 0 });
			expect(sim.rejuvenations()).toBe(0);
			expect(sim.advanceIdle(24000)).toBe(EV_DIED_EXHAUSTION);
			expect(sim.alive()).toBe(false);
		}
	});
});
