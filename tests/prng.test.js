import { describe, expect, it } from "vitest";
import { coinFlip, createRng, splitmix64Next, top32 } from "../shared/prng.js";

describe("shared splitmix64 prng", () => {
	it("matches the published vector for seed 0", () => {
		const out = splitmix64Next(0n);
		expect(out.value.toString(16)).toBe("e220a8397b1dcdaf");
		expect(out.state.toString(16)).toBe("9e3779b97f4a7c15");
	});

	it("is deterministic per seed and differs across seeds", () => {
		const run = (lo, hi, n) => {
			const rng = createRng(lo, hi);
			const out = [];
			for (let i = 0; i < n; i++) {
				out.push(coinFlip(rng));
			}
			return out.join(",");
		};
		expect(run(42, 0, 20)).toBe(run(42, 0, 20));
		expect(run(42, 0, 20)).not.toBe(run(43, 0, 20));
	});

	it("splits u64 seeds into halves like the sim", () => {
		const rng = createRng(0xd70fc135, 0x9833bca1);
		expect(top32(splitmix64Next(rng.state).value)).toBeLessThan(0x100000000);
		expect(typeof rng.state).toBe("bigint");
	});
});
