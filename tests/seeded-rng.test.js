import { readFile } from "node:fs/promises";
import { createContext, runInContext } from "node:vm";
import { describe, expect, it } from "vitest";
import { coinFlip, createRng } from "../shared/prng.js";
import { splitSeedHex } from "../shared/trace-codec.js";

// The shim is a classic script (no modules): run it in a stubbed window.
// Behavior under test: window.__rngDraws counts seeded draws only and
// window.__rngReset() clears it without perturbing the stream.
async function loadShim(search) {
	const code = await readFile("public/js/seeded-rng.js", "utf8");
	const sandbox = { window: { location: { search } } };
	createContext(sandbox);
	runInContext(code, sandbox, { filename: "seeded-rng.js" });
	return sandbox.window;
}

const SEED_HEX = "0123456789abcdef";

function expectedFlips(n) {
	const { seedLo, seedHi } = splitSeedHex(SEED_HEX);
	const rng = createRng(seedLo, seedHi);
	const out = [];
	for (let i = 0; i < n; i++) {
		out.push(coinFlip(rng));
	}
	return out;
}

describe("seeded-rng draw telemetry", () => {
	it("starts at zero and counts one seeded draw per flip", async () => {
		const win = await loadShim(`?seed=${SEED_HEX}`);
		expect(win.__rngDraws).toBe(0);
		const seen = [];
		for (let i = 0; i < 10; i++) {
			seen.push(win.__rng50());
		}
		expect(win.__rngDraws).toBe(10);
		// The counter must not perturb the stream: values stay bit-identical
		// to shared/prng.js coin flips off the same seed.
		expect(seen).toEqual(expectedFlips(10));
	});

	it("reset clears the count and restarts the stream", async () => {
		const win = await loadShim(`?seed=${SEED_HEX}`);
		for (let i = 0; i < 7; i++) {
			win.__rng50();
		}
		expect(win.__rngDraws).toBe(7);
		win.__rngReset();
		expect(win.__rngDraws).toBe(0);
		const first = win.__rng50();
		expect(win.__rngDraws).toBe(1);
		expect(first).toBe(expectedFlips(1)[0]);
	});

	it("never counts legacy fallback draws on unseeded opens", async () => {
		const win = await loadShim("?dbg=1");
		expect(win.__rngDraws).toBe(0);
		for (let i = 0; i < 5; i++) {
			expect(typeof win.__rng50()).toBe("boolean");
		}
		expect(win.__rngDraws).toBe(0);
		win.__rngReset();
		expect(win.__rngDraws).toBe(0);
	});
});
