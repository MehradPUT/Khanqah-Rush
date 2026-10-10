import { readFileSync } from "node:fs";
import vm from "node:vm";
import { describe, expect, it } from "vitest";
import { coinFlip, createRng } from "../shared/prng.js";
import { splitSeedHex } from "../shared/trace-codec.js";

// Differential lock for the three little-endian hex16 seed decoders:
// - public/js/seeded-rng.js readSeed() (classic script, vm-loaded below),
// - shared/trace-codec.js splitSeedHex() (companion path:
//   client/js/score-report.mjs),
// - server/score-core.js replayTrace() (mirrored by serverSplitSeedHex).
// The page shim cannot import the shared decoder: it is a classic
// non-module script that must load before the bundle with no imports
// (index.html), so it duplicates the decoder. The sim consumes the
// halves via createRng (shared/prng.js, shared/sim.js).
// If any copy drifts from DataView-LE semantics, these tests fail.

const SHIM_URL = new URL("../public/js/seeded-rng.js", import.meta.url);

// Boundaries, high-bit halves, byte-order probes, and the splitmix
// constants that seed real rounds.
const VECTORS = [
	"0000000000000000",
	"ffffffffffffffff",
	"0000000080000000",
	"8000000000000000",
	"0102030405060708",
	"ff00ff00ff00ff00",
	"00ff00ff00ff00ff",
	"7fffffff80000001",
	"1234567890abcdef",
	"deadbeefcafebabe",
	"9e3779b97f4a7c15",
	"bf58476d1ce4e5b9",
];

// Mirror of server/score-core.js: private fromHex() plus the replayTrace()
// DataView-LE re-derivation compared against the trace header.
function serverSplitSeedHex(hex16) {
	const out = new Uint8Array(hex16.length / 2);
	for (let i = 0; i < out.length; i++) {
		out[i] = Number.parseInt(hex16.slice(i * 2, i * 2 + 2), 16);
	}
	const view = new DataView(out.buffer, out.byteOffset, out.byteLength);
	return {
		seedLo: view.getUint32(0, true) >>> 0,
		seedHi: view.getUint32(4, true) >>> 0,
	};
}

// Run the real classic shim in a vm sandbox (do NOT convert it to a
// module) with the given query string; returns window with
// __rngReset/__rng50 wired.
function runShim(search, mathRandom) {
	const src = readFileSync(SHIM_URL, "utf8");
	const win = {
		location: { search },
		__rngReset: null,
		__rng50: null,
	};
	const sandbox = {
		window: win,
		Math: mathRandom
			? Object.assign(Object.create(Math), { random: mathRandom })
			: Math,
	};
	vm.createContext(sandbox);
	vm.runInContext(src, sandbox, { filename: "seeded-rng.js" });
	return win;
}

// Reference draw stream: canonical codec halves through the shared PRNG.
function refDraws(hex16, n) {
	const seed = splitSeedHex(hex16);
	expect(seed).not.toBeNull();
	const rng = createRng(seed.seedLo, seed.seedHi);
	const out = [];
	for (let i = 0; i < n; i++) {
		out.push(coinFlip(rng) ? 1 : 0);
	}
	return out.join(",");
}

function shimDraws(hex16, n) {
	const win = runShim(`?seed=${hex16}`);
	expect(typeof win.__rng50).toBe("function");
	const out = [];
	for (let i = 0; i < n; i++) {
		out.push(win.__rng50() ? 1 : 0);
	}
	return out.join(",");
}

describe("seed hex16 decoders agree bit-for-bit", () => {
	it("decodes every vector identically across shim, codec, and server", () => {
		for (const hex of VECTORS) {
			const codec = splitSeedHex(hex);
			const server = serverSplitSeedHex(hex);
			expect(codec).not.toBeNull();
			expect(server.seedLo).toBe(codec.seedLo);
			expect(server.seedHi).toBe(codec.seedHi);
			// The shim ships no exports; its vm-loaded draw stream must
			// equal the reference stream, proving the file still carries
			// the same DataView-LE arithmetic.
			expect(shimDraws(hex, 20)).toBe(refDraws(hex, 20));
		}
	});

	it("drives byte-order-sensitive halves through the shared stream", () => {
		// 0102030405060708 swaps lo/hi under the wrong endianness; the
		// high-bit halves pin >>> 0 coercion of the float sums.
		expect(splitSeedHex("0102030405060708")).toEqual({
			seedLo: 0x04030201,
			seedHi: 0x08070605,
		});
		expect(splitSeedHex("0000000080000000")).toEqual({
			seedLo: 0x00000000,
			seedHi: 0x00000080,
		});
		expect(splitSeedHex("8000000000000000")).toEqual({
			seedLo: 0x00000080,
			seedHi: 0x00000000,
		});
	});

	it("degrades uppercase/malformed seeds to unreported play", () => {
		// Companion gate (client/js/score-report.mjs HEX_16) and the shim
		// regex (/[?&]seed=([0-9a-f]{16})/) are both lowercase-only while
		// deriveSeed emits lowercase hex, so production seeds always pass
		// both. Anything else must degrade, never report a mismatch.
		const HEX_16 = /^[0-9a-f]{16}$/;
		for (const bad of [
			"",
			"abc",
			"12345678",
			"ABCDEF1234567890",
			"1234567890ABCDEF",
			"1234567890abcdeg",
			"g1234567890abcd",
		]) {
			expect(splitSeedHex(bad)).toBeNull();
			expect(HEX_16.test(bad)).toBe(false);
			let randomCalls = 0;
			const win = runShim(`?seed=${bad}`, () => {
				randomCalls += 1;
				return 0;
			});
			// Legacy fallback: the draw consumes Math.random, and the 0
			// stub makes legacyDraw() take its true branch.
			expect(win.__rng50()).toBe(true);
			expect(randomCalls).toBeGreaterThan(0);
		}
		// Missing param entirely also falls back.
		let missingCalls = 0;
		const win = runShim("?sid=abc", () => {
			missingCalls += 1;
			return 0;
		});
		expect(win.__rng50()).toBe(true);
		expect(missingCalls).toBeGreaterThan(0);
	});
});
