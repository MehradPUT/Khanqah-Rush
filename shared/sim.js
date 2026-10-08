/**
 * Deterministic Khanqah Rush simulation core — pure-JS port of
 * wasm/sim/src/lib.rs (the reference implementation).
 *
 * Runs anywhere: browsers, Workers edge isolates (whose V8 refuses to
 * compile WASM — hence this port for the server replay path), and node.
 * The RNG stream comes from shared/prng.js (single source).
 *
 * BIT-IDENTITY CONTRACT: every behavior here must match the Rust core
 * exactly, verified by tests/sim-parity.test.js (golden vectors +
 * randomized differential runs against the compiled WASM, heroes
 * included). Any logic change lands in BOTH implementations.
 *
 * Mechanics (ported 1:1, see docs/bundle-map.md for landmarks):
 * - segment queue of side+magnitude entries (-1/-2 LEFT, 1/2 RIGHT,
 *   0 none), spawned in pairs off a single 50/50 draw;
 * - chop shifts one entry, replenishes a pair when the queue is odd;
 * - lethal chop = branch on the player's side (score NOT incremented),
 *   shattering `|x| === 1` first (a shift with no score);
 * - stamina is a deadline timestamp: first chop sets t+4250, each
 *   survived chop adds the refill capped at now + window; the frame
 *   loop kills past the deadline (chops never check it first — a late
 *   chop while still alive is processed, an accepted sub-frame
 *   residual the sim resolves by killing before processing);
 * - score increments only on survived chops, with a float64 difficulty
 *   chain: every score % 20 === 0 shrinks window and refill ×0.95
 *   (same IEEE754 ops in the same order on every engine).
 * - heroes: Nima rejuvenation, Fargol flame + one sacrifice, Ali
 *   auto-flurry, Ahmad stacking shields, Parsa exhaustion naps,
 *   Amirhossein 2X, Erfan clutch 3X, Fateme base.
 *
 * Clock range assumption (shared with the Rust core): round clocks stay
 * far below 2^31 ms, where JS number math and Rust u32 math agree
 * exactly. Traces cap timestamps at u32 anyway.
 */

import { coinFlip, createRng } from "./prng.js";
import {
	HERO_AHMAD,
	HERO_ALI,
	HERO_AMIRHOSSEIN,
	HERO_ERFAN,
	HERO_FARGOL,
	HERO_NIMA,
	HERO_PARSA,
} from "./trace-codec.js";

export const SIM_VERSION = 2;
export const QUEUE_CAP = 16;

export const SIDE_NONE = 0;
export const SIDE_LEFT = 1;
export const SIDE_RIGHT = 2;

export const EV_ALIVE = 0;
export const EV_DIED_BRANCH = 1;
export const EV_DIED_EXHAUSTION = 2;
export const EV_INVALID_TIME = 3;
export const EV_ALREADY_DEAD = 4;

const FIRST_GRACE_MS = 4250;
const QA_MS = 8500;
const GA_MS = 250;

const REJUV_CYCLE_MS = 20_000;
const REJUV_FROM_MS = 15_000;
const REJUV_WINDOW_MS = REJUV_CYCLE_MS - REJUV_FROM_MS;

const FLAME_MS = 5000;
const FARGOL_FLAME_EVERY = 100;
const SACRIFICE_MS = 880;
const SACRIFICE_IMPACT_MS = 420;
const FLURRY_COUNT = 10;
const FLURRY_STEP_MS = 95;
const ALI_FLURRY_EVERY = 50;
const AHMAD_SHIELD_EVERY = 100;
const PARSA_NAPS = 2;
const PARSA_SLEEP_MS = 3000;

const U32_MAX = 0xffffffff;

function satAdd(a, b) {
	const sum = a + b;
	return sum > U32_MAX ? U32_MAX : sum;
}

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
	return start > U32_MAX ? null : start;
}

function collides(left, bottom) {
	return left === bottom < 0;
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
		this.hero = HERO_NIMA;
		this.rejuvenations = 0;
		this.enteredRejuv = false;
		this.qaMs = QA_MS;
		this.gaMs = GA_MS;
		this.heroChops = 0;
		this.playerLeft = false;
		this.flameStartMs = null;
		this.sacrificeUsed = false;
		this.sacrificeIgnoreUntilMs = 0;
		this.sacrificeImpactAtMs = null;
		this.sacrificeImpactLeft = false;
		this.flurryActive = false;
		this.flurryRemaining = 0;
		this.flurryNextAtMs = 0;
		this.shields = 0;
		this.sleepsUsed = 0;
		this.napStartMs = 0;
		this.suspended = false;
		// da=[0,0], then pairs while length < 11 (settles at 12).
		this.pushRaw(SIDE_NONE);
		this.pushRaw(SIDE_NONE);
		while (this.queueLen < 11) {
			this.pushPair();
		}
		return this;
	}

	setCharacter(id) {
		this.hero = id;
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

	/** One queue shift with odd-length replenish (no visuals). */
	shiftEntry() {
		if (this.queueLen % 2 === 1) {
			this.pushPair();
		}
		return this.shift();
	}

	/** Shatter a `|x| === 1` branch: same shift, no score. */
	shatterIfSmall() {
		if (this.queueLen > 0 && Math.abs(this.queue[0]) === 1) {
			this.shiftEntry();
		}
	}

	/**
	 * Branch-cleanup pattern (sacrifice impact, Ahmad save): shatter,
	 * then shift + score when the (new) bottom still collides. The
	 * bundle omits the nonzero guard on the re-check, so a NONE bottom
	 * "collides" for RIGHT-side play.
	 */
	cleanupCollide() {
		if (this.queueLen > 0) {
			const b = this.queue[0];
			if (b !== SIDE_NONE && collides(this.playerLeft, b)) {
				this.shatterIfSmall();
			}
		}
		if (this.queueLen > 0) {
			const b = this.queue[0];
			if (collides(this.playerLeft, b)) {
				this.shiftEntry();
				this.scorePoint();
			}
		}
	}

	/** One score point plus the difficulty ramp. */
	scorePoint() {
		this.score += 1;
		if (this.score % 20 === 0) {
			this.qaMs *= 0.95;
			this.gaMs *= 0.95;
		}
	}

	/** Erfan's +2 lands as one block with a single post-check. */
	scoreBonus2() {
		this.score += 2;
		if (this.score % 20 === 0) {
			this.qaMs *= 0.95;
			this.gaMs *= 0.95;
		}
	}

	refill(tMs) {
		this.deadlineMs = Math.min(this.deadlineMs + this.gaMs, tMs + this.qaMs);
	}

	pinFull(tMs) {
		this.deadlineMs = tMs + this.qaMs;
	}

	flameActiveAt(tMs) {
		return this.flameStartMs !== null && tMs - this.flameStartMs < FLAME_MS;
	}

	/** Ali's safe side: first nonzero of the bottom three, else player. */
	aliSafeSide() {
		for (let i = 0; i < 3 && i < this.queueLen; i++) {
			if (this.queue[i] !== SIDE_NONE) {
				return this.queue[i] > 0;
			}
		}
		return this.playerLeft;
	}

	/**
	 * Run pending flurry auto-chops scheduled at or below `uptoMs`.
	 * Each is a base chop on the safe side (score, refill, stamina
	 * pin) with no counter progress and no retrigger.
	 */
	flushFlurry(uptoMs) {
		while (this.alive && this.flurryActive && this.flurryNextAtMs <= uptoMs) {
			const t = this.flurryNextAtMs;
			this.shiftEntry();
			this.scorePoint();
			this.pinFull(t);
			this.playerLeft = this.aliSafeSide();
			this.flurryRemaining -= 1;
			this.flurryNextAtMs = satAdd(this.flurryNextAtMs, FLURRY_STEP_MS);
			if (this.flurryRemaining === 0) {
				this.flurryActive = false;
			}
		}
	}

	/** Sacrifice impact: applied once when the clock crosses it. */
	maybeImpact(tMs) {
		if (this.sacrificeImpactAtMs !== null && this.sacrificeImpactAtMs <= tMs) {
			this.sacrificeImpactAtMs = null;
			this.cleanupCollide();
		}
	}

	/**
	 * Clock advance plus Nima rejuvenation pinning. A jump that lands
	 * inside or past a window credits pinning for the crossed span;
	 * at most one fresh window extends survival per advance.
	 */
	advanceClock(tMs) {
		tMs >>>= 0;
		if (tMs > this.survivalMs) {
			this.survivalMs = tMs;
		}
		const prev = this.lastT;
		if (tMs > this.lastT) {
			this.lastT = tMs;
		}
		if (this.hero !== HERO_NIMA) {
			this.enteredRejuv = false;
			return;
		}
		const wasIn = inRejuvWindow(prev);
		const nowIn = inRejuvWindow(tMs);
		if (wasIn) {
			const exit = rejuvWindowExit(prev);
			const pinned = Math.min(tMs, exit) + this.qaMs;
			if (pinned > this.deadlineMs) {
				this.deadlineMs = pinned;
			}
			if (!this.enteredRejuv) {
				this.rejuvenations += 1;
			}
		} else {
			const start = firstRejuvStartAfter(prev);
			if (start !== null && start <= tMs && start <= this.deadlineMs) {
				const exit = satAdd(start, REJUV_WINDOW_MS);
				this.deadlineMs = Math.min(tMs, exit) + this.qaMs;
				this.rejuvenations += 1;
			}
		}
		this.enteredRejuv = nowIn;
	}

	/**
	 * Continuous stamina pins the frame loop applies between events
	 * (flame heat, sacrifice cinematic). Flurry pins per auto-chop;
	 * naps suspend the check outright; Nima lives in advanceClock.
	 */
	applyPins(tMs) {
		if (
			this.hero === HERO_FARGOL &&
			(this.flameActiveAt(tMs) || tMs < this.sacrificeIgnoreUntilMs)
		) {
			const pinned = tMs + this.qaMs;
			if (pinned > this.deadlineMs) {
				this.deadlineMs = pinned;
			}
		}
	}

	/**
	 * Exhaustion gate. Returns true when the round dies. Saves apply
	 * exactly as the frame-loop Va() would have fired them.
	 */
	checkExhaustion(tMs) {
		if (this.suspended || tMs <= this.deadlineMs) {
			return false;
		}
		const anchor = this.deadlineMs;
		if (this.hero === HERO_PARSA && this.sleepsUsed < PARSA_NAPS) {
			this.sleepsUsed += 1;
			this.suspended = true;
			this.napStartMs = anchor;
			this.pinFull(tMs);
			return false;
		}
		if (this.hero === HERO_AHMAD && this.shields > 0) {
			this.shields -= 1;
			this.pinFull(tMs);
			this.cleanupCollide();
			return false;
		}
		if (this.hero === HERO_FARGOL && !this.sacrificeUsed) {
			this.sacrificeUsed = true;
			this.pinFull(tMs);
			this.sacrificeIgnoreUntilMs = satAdd(anchor, SACRIFICE_MS);
			this.sacrificeImpactAtMs = satAdd(anchor, SACRIFICE_IMPACT_MS);
			this.sacrificeImpactLeft = this.playerLeft;
			return false;
		}
		this.alive = false;
		this.deathBranch = false;
		return true;
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
		const left = side === SIDE_LEFT;
		// Flurry autos at or below now go first: strict time order.
		this.flushFlurry(tMs);
		if (!this.alive) {
			return EV_ALREADY_DEAD;
		}
		// Time-driven effects land before input handling.
		this.maybeImpact(tMs);
		this.applyPins(tMs);
		// Sacrifice cinematic: inputs ignored (companion gates these;
		// the window covers stale clients and boundary races).
		if (this.hero === HERO_FARGOL && tMs < this.sacrificeIgnoreUntilMs) {
			return EV_ALIVE;
		}
		// Ali manual chops during flurry are ignored outright.
		if (this.hero === HERO_ALI && this.flurryActive) {
			return EV_ALIVE;
		}
		if (!this.started) {
			this.started = true;
			this.deadlineMs = tMs + FIRST_GRACE_MS;
		}
		// Parsa wake: a chop while waiting resumes with full stamina.
		// A chop still inside the 3 s sleep is ignored instead.
		if (this.suspended) {
			if (tMs < satAdd(this.napStartMs, PARSA_SLEEP_MS)) {
				return EV_ALIVE;
			}
			this.suspended = false;
			this.pinFull(tMs);
		}
		this.advanceClock(tMs);
		// Exhaustion at chop time: the frame loop would have fired
		// first, so saves apply without processing — except the Ahmad
		// shield save, whose cleanup already ran, letting the chop
		// through normally. Anchors use the pre-update deadline.
		if (tMs > this.deadlineMs) {
			const anchor = this.deadlineMs;
			if (this.hero === HERO_PARSA && this.sleepsUsed < PARSA_NAPS) {
				this.sleepsUsed += 1;
				this.napStartMs = anchor;
				this.pinFull(tMs);
				if (tMs < satAdd(anchor, PARSA_SLEEP_MS)) {
					this.suspended = true;
					return EV_ALIVE;
				}
			} else if (this.hero === HERO_AHMAD && this.shields > 0) {
				this.shields -= 1;
				this.pinFull(tMs);
				this.cleanupCollide();
			} else if (this.hero === HERO_FARGOL && !this.sacrificeUsed) {
				this.sacrificeUsed = true;
				this.pinFull(tMs);
				this.sacrificeIgnoreUntilMs = satAdd(anchor, SACRIFICE_MS);
				this.sacrificeImpactAtMs = satAdd(anchor, SACRIFICE_IMPACT_MS);
				this.sacrificeImpactLeft = this.playerLeft;
				return EV_ALIVE;
			} else {
				this.alive = false;
				this.deathBranch = false;
				return EV_DIED_EXHAUSTION;
			}
		}
		// Ahmad shield intercept: absorb a lethal branch (+1, extra
		// shift). Blocked chops don't advance the earn counter.
		if (this.hero === HERO_AHMAD && this.shields > 0) {
			const bottom = this.queueLen > 0 ? this.queue[0] : SIDE_NONE;
			if (bottom !== SIDE_NONE && collides(left, bottom)) {
				this.shatterIfSmall();
				this.shields -= 1;
				this.pinFull(tMs);
				this.scorePoint();
				this.shiftEntry();
				this.playerLeft = left;
				return EV_ALIVE;
			}
		}
		// Fargol flame intercept: lethal branches survive with +1.
		if (this.hero === HERO_FARGOL && this.flameActiveAt(tMs)) {
			const bottom = this.queueLen > 0 ? this.queue[0] : SIDE_NONE;
			if (bottom !== SIDE_NONE && collides(left, bottom)) {
				this.shatterIfSmall();
				this.pinFull(tMs);
				this.scorePoint();
				this.shiftEntry();
				this.playerLeft = left;
				return EV_ALIVE;
			}
		}
		// Normal branch check: peek first. A lethal shatters `|x| === 1`
		// and shifts nothing otherwise; a survived chop shifts exactly
		// once below. (Post-death queue state only matters via survival
		// saves, which manage their own shifts.)
		let bottom = SIDE_NONE;
		if (this.queueLen > 0) {
			bottom = this.queue[0];
		}
		if (bottom !== SIDE_NONE && collides(left, bottom)) {
			this.shatterIfSmall();
			if (this.hero === HERO_FARGOL && !this.sacrificeUsed) {
				// Va() sacrifice: survive, cinematic blackout, cleanup
				// at impact. The trigger chop scores nothing.
				this.sacrificeUsed = true;
				this.pinFull(tMs);
				this.sacrificeIgnoreUntilMs = satAdd(tMs, SACRIFICE_MS);
				this.sacrificeImpactAtMs = satAdd(tMs, SACRIFICE_IMPACT_MS);
				this.sacrificeImpactLeft = this.playerLeft;
				return EV_ALIVE;
			}
			this.alive = false;
			this.deathBranch = true;
			return EV_DIED_BRANCH;
		}
		// Survived chop: exactly one shift, refill before scoring —
		// the bundle refills before the `ca++` level check. No `wa()`
		// runs here, so the player side is untouched.
		this.shiftEntry();
		this.refill(tMs);
		this.scorePoint();
		switch (this.hero) {
			case HERO_FARGOL:
				if (!this.flameActiveAt(tMs)) {
					this.heroChops += 1;
					if (this.heroChops > 0 && this.heroChops % FARGOL_FLAME_EVERY === 0) {
						this.flameStartMs = tMs;
						this.pinFull(tMs);
					}
				}
				break;
			case HERO_ALI:
				if (!this.flurryActive) {
					this.heroChops += 1;
					if (this.heroChops > 0 && this.heroChops % ALI_FLURRY_EVERY === 0) {
						this.flurryActive = true;
						this.flurryRemaining = FLURRY_COUNT;
						this.flurryNextAtMs = satAdd(tMs, FLURRY_STEP_MS);
						this.pinFull(tMs);
						this.playerLeft = this.aliSafeSide();
					}
				}
				break;
			case HERO_AMIRHOSSEIN:
				this.scorePoint();
				break;
			case HERO_ERFAN:
				if ((this.deadlineMs - tMs) / this.qaMs < 0.5) {
					this.scoreBonus2();
				}
				break;
			case HERO_AHMAD:
				this.heroChops += 1;
				if (this.heroChops > 0 && this.heroChops % AHMAD_SHIELD_EVERY === 0) {
					this.shields += 1;
				}
				break;
			default:
				break;
		}
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
		this.flushFlurry(tMs);
		if (!this.alive) {
			return EV_ALREADY_DEAD;
		}
		this.maybeImpact(tMs);
		this.advanceClock(tMs);
		this.applyPins(tMs);
		if (this.suspended) {
			return EV_ALIVE;
		}
		if (this.checkExhaustion(tMs)) {
			return EV_DIED_EXHAUSTION;
		}
		return EV_ALIVE;
	}

	/** Milliseconds of stamina left at the current clock. */
	staminaLeftMs() {
		if (!this.alive) {
			return 0;
		}
		return Math.max(0, this.deadlineMs - this.lastT);
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
