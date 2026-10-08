import { describe, expect, it } from "vitest";
import { loadSim, SIM_LEFT, SIM_RIGHT } from "../client/js/sim-loader.mjs";
import { CHAR_NIMA, EV_ALIVE, SIM_VERSION, Sim } from "../shared/sim.js";

// Bit-identity contract between the Rust reference core (wasm/sim) and
// the pure-JS port (shared/sim.js) the server replays with. The WASM
// artifact is the oracle; the JS port must agree on every observable.
describe("sim js/wasm parity", () => {
	async function loadWasm() {
		const { readFile } = await import("node:fs/promises");
		const { existsSync } = await import("node:fs");
		const path = "public/wasm/sim.wasm";
		if (!existsSync(path)) {
			return null;
		}
		const bytes = await readFile(path);
		const sim = await loadSim(
			async () => new Response(bytes, { status: 200 }),
			"/",
		);
		return sim;
	}

	function splitSeed(seed) {
		return { lo: seed >>> 0, hi: Math.floor(seed / 2 ** 32) >>> 0 };
	}

	function snapshotWasm(w) {
		return {
			score: w.score(),
			alive: w.alive(),
			death: w.deathReason(),
			survival: w.survivalMs(),
			rejuv: w.rejuvenations(),
			segs: Array.from(w.segments() ?? []),
		};
	}

	function snapshotJs(j) {
		return {
			score: j.score,
			alive: j.alive,
			death: j.deathReason(),
			survival: j.survivalMs,
			rejuv: j.rejuvenations,
			segs: j.segments(),
		};
	}

	it("matches the reset layout on several seeds", async () => {
		const w = await loadWasm();
		if (!w) {
			return;
		}
		for (const seed of [0, 1, 7, 42, 12345, 999, 2 ** 31 + 7, 2 ** 48 - 1]) {
			const { lo, hi } = splitSeed(seed);
			w.reset(lo, hi);
			const j = new Sim();
			j.reset(lo, hi);
			expect(snapshotJs(j)).toEqual(snapshotWasm(w));
			expect(j.segments().slice(0, 2)).toEqual([0, 0]);
			expect(j.segments().length).toBe(12);
		}
	});

	it("matches the golden alternating run", async () => {
		const w = await loadWasm();
		if (!w) {
			return;
		}
		w.reset(42, 0);
		const j = new Sim();
		j.reset(42, 0);
		let t = 0;
		for (let i = 0; i < 60; i++) {
			t += 200;
			const side = i % 2 === 0 ? SIM_LEFT : SIM_RIGHT;
			const evW = w.chop(side, t);
			const evJ = j.chop(side, t);
			expect(evJ).toBe(evW);
			if (evW !== EV_ALIVE) {
				break;
			}
		}
		expect(snapshotJs(j)).toEqual(snapshotWasm(w));
		expect(j.score).toBe(3);
		expect(j.alive).toBe(false);
	});

	it("matches rejuvenation play on both heroes", async () => {
		const w = await loadWasm();
		if (!w || typeof w.setCharacter !== "function") {
			return;
		}
		for (const character of [CHAR_NIMA, 1]) {
			w.reset(42, 0);
			w.setCharacter(character);
			const j = new Sim();
			j.reset(42, 0);
			j.setCharacter(character);
			let t = 0;
			for (let i = 0; i < 100; i++) {
				t += 150;
				const bottom = j.segments()[0] ?? 0;
				const side = bottom < 0 ? SIM_RIGHT : SIM_LEFT;
				expect(j.chop(side, t)).toBe(w.chop(side, t));
			}
			expect(snapshotJs(j)).toEqual(snapshotWasm(w));
			expect(j.advanceIdle(24000)).toBe(w.advanceIdle(24000));
			expect(snapshotJs(j)).toEqual(snapshotWasm(w));
		}
		// Counter across two windows on a long safe run.
		w.reset(7, 0);
		const j = new Sim();
		j.reset(7, 0);
		let t = 0;
		for (let i = 0; i < 250; i++) {
			t += 150;
			const bottom = j.segments()[0] ?? 0;
			const side = bottom < 0 ? SIM_RIGHT : SIM_LEFT;
			const evJ = j.chop(side, t);
			expect(evJ).toBe(w.chop(side, t));
			if (evJ !== EV_ALIVE) {
				break;
			}
		}
		expect(j.rejuvenations).toBe(w.rejuvenations());
		expect(j.rejuvenations).toBe(2);
	});

	it("matches randomized scripts lockstep", async () => {
		const w = await loadWasm();
		if (!w || typeof w.setCharacter !== "function") {
			return;
		}
		// Deterministic LCG for script generation (test-only, any stream).
		let lcg = 0x12345678;
		const rand = (n) => {
			lcg = (lcg * 1103515245 + 12345) & 0x7fffffff;
			return lcg % n;
		};
		for (let round = 0; round < 40; round++) {
			const seed = rand(2 ** 31) * 65537 + rand(2 ** 16);
			const character = rand(2);
			const { lo, hi } = splitSeed(seed);
			w.reset(lo, hi);
			w.setCharacter(character);
			const j = new Sim();
			j.reset(lo, hi);
			j.setCharacter(character);
			let t = 0;
			const inputs = 50 + rand(250);
			for (let i = 0; i < inputs; i++) {
				const roll = rand(10);
				if (roll < 2) {
					// Idle jump, sometimes across whole windows.
					t += [100, 500, 2000, 9000, 25000][rand(5)];
					expect(j.advanceIdle(t), `round ${round} idle ${i}`).toBe(
						w.advanceIdle(t),
					);
				} else {
					t += rand(3000);
					const side = rand(2) === 0 ? SIM_LEFT : SIM_RIGHT;
					expect(j.chop(side, t), `round ${round} chop ${i}`).toBe(
						w.chop(side, t),
					);
				}
				expect(snapshotJs(j), `round ${round} step ${i}`).toEqual(
					snapshotWasm(w),
				);
				if (!j.alive) {
					break;
				}
			}
		}
		expect(SIM_VERSION).toBe(2);
	});
});
