/**
 * Loader for the deterministic simulation core (wire v1).
 * Same pattern as the signer: plain WebAssembly, null on absence.
 * Side encoding: 1 = LEFT, 2 = RIGHT.
 */

export const SIM_WIRE_VERSION = 1;
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

export interface Sim {
	version(): number;
	reset(seedLo: number, seedHi: number): void;
	chop(side: number, tMs: number): number;
	advanceIdle(tMs: number): number;
	score(): number;
	staminaMilli(): number;
	phase(): number;
	survivalMs(): number;
	rejuvenations(): number;
	alive(): boolean;
	deathReason(): number;
	segmentCount(): number;
	segments(): Int8Array;
}

interface RawSimExports {
	sim_version: () => number;
	sim_reset: (lo: number, hi: number) => void;
	sim_chop: (side: number, t: number) => number;
	sim_advance_idle: (t: number) => number;
	sim_score: () => number;
	sim_stamina_milli: () => number;
	sim_phase: () => number;
	sim_survival_ms: () => bigint;
	sim_rejuvenations: () => number;
	sim_alive: () => number;
	sim_death_reason: () => number;
	sim_segments_ptr: () => number;
	sim_segments_len: () => number;
	memory: WebAssembly.Memory;
}

const REQUIRED: (keyof RawSimExports)[] = [
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

function wrap(exports: WebAssembly.Exports): Sim | null {
	const raw = exports as unknown as Partial<RawSimExports>;
	if (raw.sim_version?.() !== SIM_WIRE_VERSION) {
		return null;
	}
	if (REQUIRED.some((k) => raw[k] === undefined)) {
		return null;
	}
	const r = raw as RawSimExports;
	return {
		version: () => r.sim_version(),
		reset: (lo, hi) => r.sim_reset(lo, hi),
		chop: (side, t) => r.sim_chop(side, t),
		advanceIdle: (t) => r.sim_advance_idle(t),
		score: () => r.sim_score(),
		staminaMilli: () => r.sim_stamina_milli(),
		phase: () => r.sim_phase(),
		survivalMs: () => Number(r.sim_survival_ms()),
		rejuvenations: () => r.sim_rejuvenations(),
		alive: () => r.sim_alive() === 1,
		deathReason: () => r.sim_death_reason(),
		segmentCount: () => r.sim_segments_len(),
		segments: () =>
			new Int8Array(
				r.memory.buffer.slice(
					r.sim_segments_ptr(),
					r.sim_segments_ptr() + r.sim_segments_len(),
				),
			),
	};
}

export async function loadSim(
	fetchImpl: typeof fetch = fetch,
	base: string = import.meta.env.BASE_URL,
): Promise<Sim | null> {
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
