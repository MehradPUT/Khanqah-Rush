/**
 * Seeded spawn stream for the legacy bundle game (classic script — must
 * load BEFORE js/main.js; no imports, no modules).
 *
 * The bundle draws branch layouts from Math.random(), which no server can
 * reproduce. This shim gives those two draw sites a deterministic stream:
 * splitmix64 (integer BigInt math — exact on every engine, bit-identical
 * to wasm/sim and shared/prng.js) seeded from the `seed` launch param.
 *
 * - With `?seed=<hex16>`: draws come from the seeded stream. The companion
 *   resets it every round via window.__rngReset() (clearing window.__rngDraws).
 * - Without it (direct/local opens): legacy Math.random() behavior, game
 *   runs local-only as before.
 */
(() => {
	var MASK64 = (1n << 64n) - 1n;
	var INCREMENT = 0x9e3779b97f4a7c15n;

	function splitmixNext(state) {
		var s = (state + INCREMENT) & MASK64;
		var z = s;
		z = ((z ^ (z >> 30n)) * 0xbf58476d1ce4e5b9n) & MASK64;
		z = ((z ^ (z >> 27n)) * 0x94d049bb133111ebn) & MASK64;
		return { state: s, value: (z ^ (z >> 31n)) & MASK64 };
	}

	function readSeed() {
		try {
			const m = /[?&]seed=([0-9a-f]{16})/.exec(window.location.search);
			if (!m) {
				return null;
			}
			const bytes = [];
			for (let i = 0; i < 8; i++) {
				bytes.push(parseInt(m[1].substr(i * 2, 2), 16));
			}
			let lo = 0;
			let hi = 0;
			for (let j = 0; j < 4; j++) {
				lo += bytes[j] * 256 ** j;
				hi += bytes[j + 4] * 256 ** j;
			}
			return { lo: lo >>> 0, hi: hi >>> 0 };
		} catch {
			return null;
		}
	}

	// NOTE: reconstructed as (hi * 2^32 + lo) to stay within double
	// precision only when reassembled as BigInt below.
	var seed = readSeed();
	var state = null;
	if (seed) {
		state = (BigInt(seed.hi) << 32n) | BigInt(seed.lo);
	}

	// Dev-only draw telemetry (see docs/debugging.md): seeded draws
	// consumed since load or the last reset. Legacy fallback draws
	// bypass the stream and are never counted.
	window.__rngDraws = 0;

	function draw() {
		var out = splitmixNext(state);
		state = out.state;
		window.__rngDraws += 1;
		return Number((out.value >> 32n) & 0xffffffffn) < 0x80000000;
	}

	function legacyDraw() {
		return 500 >= Math.floor(1e3 * Math.random() + 1);
	}

	window.__rngReset = () => {
		if (seed) {
			state = (BigInt(seed.hi) << 32n) | BigInt(seed.lo);
		}
		window.__rngDraws = 0;
	};

	window.__rng50 = () => {
		if (state === null) {
			return legacyDraw();
		}
		return draw();
	};
})();
