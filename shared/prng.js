/**
 * Deterministic splitmix64 PRNG shared by the page bootstrap, tests, and
 * (by port) any future language implementation.
 *
 * Integer-only BigInt arithmetic — exact on every engine, unlike
 * float-based `Math.random()` shims. The stream contract both sides must
 * honor:
 * - state starts at the 64-bit seed;
 * - each draw: state += 0x9E3779B97F4A7C15 (mod 2^64), then mix;
 * - a "coin flip" consumes ONE draw and tests the top 32 bits < 2^31.
 * Reference: Steele, Lea & Flood (2014); seed 0 yields 0xe220a8397b1dcdaf.
 */

const MASK64 = (1n << 64n) - 1n;
const INCREMENT = 0x9e3779b97f4a7c15n;

export function splitmix64Next(state) {
	let z = (state + INCREMENT) & MASK64;
	z = ((z ^ (z >> 30n)) * 0xbf58476d1ce4e5b9n) & MASK64;
	z = ((z ^ (z >> 27n)) * 0x94d049bb133111ebn) & MASK64;
	return { state: (state + INCREMENT) & MASK64, value: (z ^ (z >> 31n)) & MASK64 };
}

export function top32(value) {
	return Number((value >> 32n) & 0xffffffffn);
}

/** One 50/50 draw mirroring the bundle's `500>=Math.floor(1E3*r+1)`. */
export function coinFlip(rng) {
	const next = splitmix64Next(rng.state);
	rng.state = next.state;
	return top32(next.value) < 0x80000000;
}

export function createRng(seedLo, seedHi) {
	const seed =
		(BigInt(seedHi >>> 0) << 32n) | BigInt(seedLo >>> 0);
	return { state: seed };
}
