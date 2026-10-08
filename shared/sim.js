/**
 * Deterministic Khanqah Rush simulation core — pure-JS port of
 * wasm/sim/src/lib.rs (the reference implementation).
 *
 * Runs anywhere: browsers, Workers edge isolates (whose V8 refuses to
 * compile WASM — hence this port for the server replay path), and node.
 * Integer-only; the RNG stream comes from shared/prng.js (single source).
 *
 * BIT-IDENTITY CONTRACT: every behavior here must match the Rust core
 * exactly, verified by tests/sim-parity.test.js (golden vectors +
 * randomized differential runs against the compiled WASM). Any logic
 * change lands in BOTH implementations with updated goldens.
 *
 * Mechanics (ported 1:1):
 * - segment queue of side+magnitude entries (-1/-2 LEFT, 1/2 RIGHT,
 *   0 none), spawned in pairs off a single 50/50 draw;
 * - chop shifts one entry, replenishes a pair when the queue is odd;
 * - lethal chop = branch on the player's side (score NOT incremented);
 * - stamina is a deadline timestamp: first chop sets t+4250, each
 *   survived chop adds 250 ms capped at t+8500;
 * - Nima rejuvenation: 20 s cycle, deadline pinned to now + 8500 ms
 *   while the cycle position sits at >= 15 s, including windows crossed
 *   mid-jump (at most one fresh window extends survival per advance).
 *
 * Clock range assumption (shared with the Rust core): round clocks stay
 * far below 2^31 ms, where JS number math and Rust u32 math agree
 * exactly. Traces cap timestamps at u32 anyway.
 */

import { coinFlip, createRng } from "./prng.js";

export const SIM_VERSION = 2;
export const QUEUE_CAP = 16;

export const SIDE_NONE = 0;
export const SIDE_LEFT = 1;
export const SIDE_RIGHT = 2;

export const CHAR_NIMA = 0;

export const EV_ALIVE = 0;
export const EV_DIED_BRANCH = 1;
export const EV_DIED_EXHAUSTION = 2;
export const EV_INVALID_TIME = 3;
export const EV_ALREADY_DEAD = 4;

const FIRST_GRACE_MS = 4250;
const CHOP_REFILL_MS = 250;
const MAX_DEADLINE_AHEAD_MS = 8500;

const REJUV_CYCLE_MS = 20_000;
const REJUV_FROM_MS = 15_000;
const REJUV_WINDOW_MS = REJUV_CYCLE_MS - REJUV_FROM_MS;

function inRejuvWindow(tMs) {
	return tMs % REJUV_CYCLE_MS >= REJUV_FROM_MS;
}

function rejuvWindowExit(tMs) {
	return tMs - (tMs % REJUV_CYCLE_MS) + REJUV_CYCLE_MS;
}

function firstRejuvStartAfter(tMs) {
	const k =
		tMs < REJUV_FROM_MS
			? 0
			: Math.floor((tMs - REJUV_FROM_MS) / REJUV_CYCLE_MS) + 1;
	const start = k * REJUV_CYCLE_MS + REJUV_FROM_MS;
	return start > 0xffffffff ? null : start;
}

export class Sim {
	constructor() {
		this.reset(0, 0);
	}

	reset(seedLo, seedHi) {
		this.rng = createRng(seedLo, seedHi);
		this.score = 0;
		this.deadlineMs = FIRST_GRACE_MS;
		this.started = false;
		this.survivalMs = 0;
		this.alive = true;
		this.deathBranch = false;
		this.lastT = 0;
		this.queue = new Array(QUEUE_CAP).fill(SIDE_NONE);
		this.queueLen = 0;
		this.character = CHAR_NIMA;
		this.rejuvenations = 0;
		this.enteredRejuv = false;
		// da=[0,0], then pairs while length < 11 (settles at 12).
		this.pushRaw(SIDE_NONE);
		this.pushRaw(SIDE_NONE);
		while (this.queueLen < 11) {
			this.pushPair();
		}
		return this;
	}

	setCharacter(id) {
		this.character = id;
	}

	pushRaw(v) {
		this.queue[this.queueLen] = v;
		this.queueLen += 1;
	}

	pushPair() {
		if (coinFlip(this.rng)) {
			this.pushRaw(-1);
			this.pushRaw(-2);
		} else {
			this.pushRaw(1);
			this.pushRaw(2);
		}
	}

	shift() {
		const bottom = this.queue[0];
		for (let i = 0; i + 1 < this.queueLen; i++) {
			this.queue[i] = this.queue[i + 1];
		}
		this.queueLen -= 1;
		return bottom;
	}

	/** Advance the clock; returns true on exhaustion death. */
	advanceTo(tMs) {
		tMs >>>= 0;
		if (tMs > this.survivalMs) {
			this.survivalMs = tMs;
		}
		const prev = this.lastT;
		if (tMs > this.lastT) {
			this.lastT = tMs;
		}
		if (this.alive && this.character === CHAR_NIMA) {
			const wasIn = inRejuvWindow(prev);
			const nowIn = inRejuvWindow(tMs);
			if (wasIn) {
				const exit = rejuvWindowExit(prev);
				const pinned = Math.min(tMs, exit) + MAX_DEADLINE_AHEAD_MS;
				if (pinned > this.deadlineMs) {
					this.deadlineMs = pinned;
				}
				if (!this.enteredRejuv) {
					this.rejuvenations += 1;
				}
			} else {
				const start = firstRejuvStartAfter(prev);
				if (start !== null && start <= tMs && start <= this.deadlineMs) {
					const exit = start + REJUV_WINDOW_MS;
					this.deadlineMs = Math.min(tMs, exit) + MAX_DEADLINE_AHEAD_MS;
					this.rejuvenations += 1;
				}
			}
			this.enteredRejuv = nowIn;
			if (tMs > this.deadlineMs) {
				this.alive = false;
				this.deathBranch = false;
				return true;
			}
		} else if (this.alive && tMs > this.deadlineMs) {
			this.alive = false;
			this.deathBranch = false;
			return true;
		}
		return !this.alive;
	}

	/** Chop: side 1 = LEFT, 2 = RIGHT. Returns an EV_* code. */
	chop(side, tMs) {
		tMs >>>= 0;
		if (!this.alive) {
			return EV_ALREADY_DEAD;
		}
		if (tMs < this.lastT) {
			return EV_INVALID_TIME;
		}
		const s = side === 1 ? SIDE_LEFT : SIDE_RIGHT;
		if (!this.started) {
			this.started = true;
			this.deadlineMs = tMs + FIRST_GRACE_MS;
		}
		if (this.advanceTo(tMs)) {
			return EV_DIED_EXHAUSTION;
		}
		if (this.queueLen % 2 === 1) {
			this.pushPair();
		}
		const bottom = this.shift();
		if (bottom !== SIDE_NONE && (s === SIDE_LEFT) === bottom < 0) {
			this.alive = false;
			this.deathBranch = true;
			return EV_DIED_BRANCH;
		}
		this.score += 1;
		const refilled = this.deadlineMs + CHOP_REFILL_MS;
		const capped = tMs + MAX_DEADLINE_AHEAD_MS;
		this.deadlineMs = refilled < capped ? refilled : capped;
		return EV_ALIVE;
	}

	/** Idle clock advance (no input). Returns EV_* like chop(). */
	advanceIdle(tMs) {
		tMs >>>= 0;
		if (!this.alive) {
			return EV_ALREADY_DEAD;
		}
		if (tMs < this.lastT) {
			return EV_INVALID_TIME;
		}
		if (this.advanceTo(tMs)) {
			return EV_DIED_EXHAUSTION;
		}
		return EV_ALIVE;
	}

	/** Milliseconds of stamina left at the current clock. */
	staminaLeftMs() {
		if (!this.alive) {
			return 0;
		}
		return this.deadlineMs > this.lastT ? this.deadlineMs - this.lastT : 0;
	}

	/** 0 = alive/none, 1 = branch, 2 = exhaustion. */
	deathReason() {
		if (this.alive) {
			return 0;
		}
		return this.deathBranch ? 1 : 2;
	}

	/** Live queue contents (bottom first). */
	segments() {
		return this.queue.slice(0, this.queueLen);
	}
}
