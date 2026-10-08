/**
 * Loader for the deterministic simulation core (wire v1).
 * Plain JavaScript for the legacy page (no TS pipeline): same pattern as
 * the signer, null on absence. Side encoding: 1 = LEFT, 2 = RIGHT.
 *
 * @typedef {object} Sim
 * @property {() => number} version
 * @property {(lo: number, hi: number) => void} reset
 * @property {(id: number) => void} [setCharacter]
 * @property {(side: number, tMs: number) => number} chop
 * @property {(tMs: number) => number} advanceIdle
 * @property {() => number} score
 * @property {() => number} staminaMilli
 * @property {() => number} phase
 * @property {() => number} survivalMs
 * @property {() => number} rejuvenations
 * @property {() => boolean} alive
 * @property {() => number} deathReason
 * @property {() => number} segmentCount
 * @property {() => Int8Array} segments
 */

export const SIM_WIRE_VERSION = 2;
export const SIM_LEFT = 1;
export const SIM_RIGHT = 2;

export const EV_ALIVE = 0;
export const EV_DIED_BRANCH = 1;
export const EV_DIED_EXHAUSTION = 2;
export const EV_INVALID_TIME = 3;
export const EV_ALREADY_DEAD = 4;

export const DEATH_NONE = 0;
export const DEATH_BRANCH = 1;
export const DEATH_EXHAUSTION = 2;

// Canonical WASM export surface. Reused by server replay validation so
// both sides agree on the artifact shape (single source).
export const SIM_REQUIRED_EXPORTS = [
	"sim_version",
	"sim_reset",
	"sim_chop",
	"sim_advance_idle",
	"sim_score",
	"sim_stamina_milli",
	"sim_phase",
	"sim_survival_ms",
	"sim_rejuvenations",
	"sim_alive",
	"sim_death_reason",
	"sim_segments_ptr",
	"sim_segments_len",
	"memory",
];

const REQUIRED = SIM_REQUIRED_EXPORTS;

function wrap(exports) {
	const raw = exports;
	if (
		typeof raw.sim_version !== "function" ||
		raw.sim_version() !== SIM_WIRE_VERSION ||
		REQUIRED.some((k) => raw[k] === undefined)
	) {
		return null;
	}
	const memory = raw.memory;
	return {
		version: () => raw.sim_version(),
		reset: (lo, hi) => raw.sim_reset(lo, hi),
		// Optional: older artifacts predate the hero model. The sim
		// defaults to Nima (id 0), so absence only matters for
		// non-Nima rounds, which replay-mismatch by design.
		...(typeof raw.sim_set_character === "function"
			? { setCharacter: (id) => raw.sim_set_character(id) }
			: {}),
		chop: (side, t) => raw.sim_chop(side, t),
		advanceIdle: (t) => raw.sim_advance_idle(t),
		score: () => raw.sim_score(),
		staminaMilli: () => raw.sim_stamina_milli(),
		phase: () => raw.sim_phase(),
		survivalMs: () => Number(raw.sim_survival_ms()),
		rejuvenations: () => raw.sim_rejuvenations(),
		alive: () => raw.sim_alive() === 1,
		deathReason: () => raw.sim_death_reason(),
		segmentCount: () => raw.sim_segments_len(),
		segments: () =>
			new Int8Array(
				memory.buffer.slice(
					raw.sim_segments_ptr(),
					raw.sim_segments_ptr() + raw.sim_segments_len(),
				),
			),
	};
}

export async function loadSim(
	fetchImpl = (...args) => fetch(...args),
	base = "/",
) {
	try {
		const response = await fetchImpl(`${base}wasm/sim.wasm`);
		if (!response.ok) {
			return null;
		}
		const bytes = await response.arrayBuffer();
		const { instance } = await WebAssembly.instantiate(bytes);
		return wrap(instance.exports);
	} catch {
		return null;
	}
}
