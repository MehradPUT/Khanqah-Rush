//! Khanqah Rush deterministic simulation core.
//!
//! Integer-only game logic shared bit-identically by the browser (WASM) and
//! the server replay path (same artifact on Workers, native binary for local
//! checks). No floats, no wall clock, no allocator: outcomes are a pure
//! function of `(seed, inputs)`.
//!
//! Time advances in fixed 10 ms steps driven by caller-supplied timestamps,
//! so replays need only the chop trace, never frame data. Cosmetic systems
//! (particles, flying blocks, rendering, audio) stay in TypeScript.

pub const SIM_VERSION: u32 = 1;
pub const SEGMENTS: usize = 10;
pub const STEP_MS: u32 = 10;

pub const SIDE_NONE: i8 = 0;
pub const SIDE_LEFT: i8 = 1;
pub const SIDE_RIGHT: i8 = 2;

// Event codes returned by chop/advance.
pub const EV_ALIVE: u32 = 0;
pub const EV_DIED_BRANCH: u32 = 1;
pub const EV_DIED_EXHAUSTION: u32 = 2;
pub const EV_INVALID_TIME: u32 = 3;
pub const EV_ALREADY_DEAD: u32 = 4;

// Spawn distribution, ported from Pillar.addSegment. Thresholds are
// fractions of 2^32 applied to the top 32 bits of splitmix64 output,
// so no floating point is involved anywhere.
const SPAWN_THRESH: u32 = 2362232012; // 0.55
const REPEAT_THRESH: u32 = 2147483648; // 0.50
const SAME_SIDE_THRESH: u32 = 1503238553; // 0.35

const CHARGE_MS: u32 = 30_000;
const ACTIVE_MS: u32 = 5_000;
const STAMINA_FULL: i32 = 1000;
const CHOP_REFILL_MILLI: i32 = 65;
const BASE_DRAIN_MILLI_PER_SEC: i32 = 160;
const SCORE_DRAIN_MAX_MILLI_PER_SEC: u32 = 220;

fn splitmix64(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

fn draw_u32(rng: &mut u64) -> u32 {
    (splitmix64(rng) >> 32) as u32
}

/// One branch-layout draw. Mirrors Pillar.addSegment exactly, including RNG
/// consumption order (spawn roll first, conditional second roll).
fn gen_segment(rng: &mut u64, last_side: i8) -> (i8, i8) {
    let mut side = SIDE_NONE;
    if draw_u32(rng) < SPAWN_THRESH {
        side = if last_side == SIDE_NONE {
            if draw_u32(rng) < REPEAT_THRESH {
                SIDE_LEFT
            } else {
                SIDE_RIGHT
            }
        } else if last_side == SIDE_LEFT {
            if draw_u32(rng) < SAME_SIDE_THRESH {
                SIDE_LEFT
            } else {
                SIDE_NONE
            }
        } else if draw_u32(rng) < SAME_SIDE_THRESH {
            SIDE_RIGHT
        } else {
            SIDE_NONE
        };
    }
    (side, side)
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Sim {
    rng: u64,
    pub score: u32,
    pub stamina_milli: i32,
    pub phase_young: bool,
    pub charge_ms: u32,
    pub active_ms: u32,
    pub survival_ms: u64,
    pub rejuvenations: u32,
    pub alive: bool,
    pub death_branch: bool,
    pub last_t_ms: u32,
    pub segments: [i8; SEGMENTS],
    pub last_side: i8,
}

impl Sim {
    pub fn new(seed: u64) -> Self {
        let mut sim = Self {
            rng: seed,
            score: 0,
            stamina_milli: STAMINA_FULL,
            phase_young: false,
            charge_ms: 0,
            active_ms: 0,
            survival_ms: 0,
            rejuvenations: 0,
            alive: true,
            death_branch: false,
            last_t_ms: 0,
            segments: [SIDE_NONE; SEGMENTS],
            last_side: SIDE_NONE,
        };
        // First 3 segments always safe, then fill like Pillar.reset().
        for i in 3..SEGMENTS {
            let (side, last) = gen_segment(&mut sim.rng, sim.last_side);
            sim.segments[i] = side;
            sim.last_side = last;
        }
        sim
    }

    /// Advance the clock to `t_ms` in fixed steps. Returns true if the
    /// player died of exhaustion during the gap. Sub-step remainders carry
    /// over implicitly via last_t_ms.
    fn advance_to(&mut self, t_ms: u32) -> bool {
        while self.alive && self.last_t_ms.saturating_add(STEP_MS) <= t_ms {
            self.step();
        }
        if self.alive {
            let done = self.last_t_ms + (t_ms.saturating_sub(self.last_t_ms) / STEP_MS) * STEP_MS;
            self.last_t_ms = done;
        }
        !self.alive
    }

    fn step(&mut self) {
        self.survival_ms += STEP_MS as u64;
        self.last_t_ms += STEP_MS;
        if !self.phase_young {
            self.charge_ms += STEP_MS;
            if self.charge_ms >= CHARGE_MS {
                self.phase_young = true;
                self.active_ms = ACTIVE_MS;
                self.charge_ms = 0;
                self.rejuvenations += 1;
            }
            let extra = (self.score.saturating_mul(12) / 10).min(SCORE_DRAIN_MAX_MILLI_PER_SEC);
            let drain = BASE_DRAIN_MILLI_PER_SEC + extra as i32;
            self.stamina_milli -= drain * STEP_MS as i32 / 1000;
            if self.stamina_milli <= 0 {
                self.stamina_milli = 0;
                self.alive = false;
                self.death_branch = false;
            }
        } else {
            self.stamina_milli = STAMINA_FULL;
            self.active_ms = self.active_ms.saturating_sub(STEP_MS);
            if self.active_ms == 0 {
                self.phase_young = false;
                self.charge_ms = 0;
            }
        }
    }

    /// Apply a chop. Returns an EV_* code.
    pub fn chop(&mut self, side: i8, t_ms: u32) -> u32 {
        if !self.alive {
            return EV_ALREADY_DEAD;
        }
        if t_ms < self.last_t_ms {
            return EV_INVALID_TIME;
        }
        if self.advance_to(t_ms) {
            return EV_DIED_EXHAUSTION;
        }
        let bottom = self.segments[0];
        self.segments.copy_within(1.., 0);
        let (side_new, last) = gen_segment(&mut self.rng, self.last_side);
        self.segments[SEGMENTS - 1] = side_new;
        self.last_side = last;
        self.score += 1;
        if self.phase_young {
            self.stamina_milli = STAMINA_FULL;
        } else {
            self.stamina_milli = (self.stamina_milli + CHOP_REFILL_MILLI).min(STAMINA_FULL);
        }
        if bottom == side {
            self.alive = false;
            self.death_branch = true;
            return EV_DIED_BRANCH;
        }
        EV_ALIVE
    }

    /// Idle clock advance (no input). Returns EV_* like chop().
    pub fn advance_idle(&mut self, t_ms: u32) -> u32 {
        if !self.alive {
            return EV_ALREADY_DEAD;
        }
        if t_ms < self.last_t_ms {
            return EV_INVALID_TIME;
        }
        if self.advance_to(t_ms) {
            return EV_DIED_EXHAUSTION;
        }
        EV_ALIVE
    }
}

// ---- C ABI: single static instance (one game session per page) ----

static mut GAME: Option<Sim> = None;

fn game_mut() -> &'static mut Sim {
    unsafe {
        if (*core::ptr::addr_of!(GAME)).is_none() {
            *core::ptr::addr_of_mut!(GAME) = Some(Sim::new(0));
        }
        (*core::ptr::addr_of_mut!(GAME)).as_mut().unwrap()
    }
}

/// Start (or restart) a session. Seed comes from the server at launch.
#[no_mangle]
pub extern "C" fn sim_reset(seed_lo: u32, seed_hi: u32) {
    let seed = ((seed_hi as u64) << 32) | seed_lo as u64;
    unsafe {
        *core::ptr::addr_of_mut!(GAME) = Some(Sim::new(seed));
    }
}

#[no_mangle]
pub extern "C" fn sim_version() -> u32 {
    SIM_VERSION
}

/// Chop: side 1 = LEFT, 2 = RIGHT. Returns EV_*.
#[no_mangle]
pub extern "C" fn sim_chop(side: u8, t_ms: u32) -> u32 {
    let side = if side == 1 { SIDE_LEFT } else { SIDE_RIGHT };
    game_mut().chop(side, t_ms)
}

/// Idle advance to t_ms. Returns EV_*.
#[no_mangle]
pub extern "C" fn sim_advance_idle(t_ms: u32) -> u32 {
    game_mut().advance_idle(t_ms)
}

#[no_mangle]
pub extern "C" fn sim_score() -> u32 {
    game_mut().score
}

#[no_mangle]
pub extern "C" fn sim_stamina_milli() -> i32 {
    game_mut().stamina_milli
}

/// 0 = old, 1 = young.
#[no_mangle]
pub extern "C" fn sim_phase() -> u32 {
    u32::from(game_mut().phase_young)
}

#[no_mangle]
pub extern "C" fn sim_survival_ms() -> u64 {
    game_mut().survival_ms
}

#[no_mangle]
pub extern "C" fn sim_rejuvenations() -> u32 {
    game_mut().rejuvenations
}

/// 1 = alive, 0 = dead.
#[no_mangle]
pub extern "C" fn sim_alive() -> u32 {
    u32::from(game_mut().alive)
}

/// 0 = alive/none, 1 = branch, 2 = exhaustion.
#[no_mangle]
pub extern "C" fn sim_death_reason() -> u32 {
    let game = game_mut();
    if game.alive {
        0
    } else if game.death_branch {
        1
    } else {
        2
    }
}

#[no_mangle]
pub extern "C" fn sim_segments_ptr() -> *const i8 {
    game_mut().segments.as_ptr()
}

#[no_mangle]
pub extern "C" fn sim_segments_len() -> usize {
    SEGMENTS
}

#[cfg(test)]
mod tests {
    use super::*;

    fn play(seed: u64, sides: &[i8], step_ms: u32) -> Sim {
        let mut sim = Sim::new(seed);
        let mut t = 0u32;
        for &side in sides {
            t += step_ms;
            let ev = sim.chop(side, t);
            if ev != EV_ALIVE {
                break;
            }
        }
        sim
    }

    #[test]
    fn reset_layout_is_deterministic() {
        let a = Sim::new(12345);
        let b = Sim::new(12345);
        assert_eq!(a, b);
        assert_eq!(&a.segments[..3], &[SIDE_NONE; 3]);
        assert_ne!(Sim::new(999), a);
    }

    #[test]
    fn golden_run_matches_recorded_values() {
        // Alternating sides every 200 ms on seed 42. Golden values below
        // were recorded from this implementation; the vitest suite asserts
        // the same numbers against the compiled WASM build, proving the
        // artifact behaves identically to native.
        let sides = [SIDE_LEFT, SIDE_RIGHT];
        let mut pattern = Vec::new();
        for i in 0..60 {
            pattern.push(sides[i % 2]);
        }
        let sim = play(42, &pattern, 200);
        assert_eq!(sim.score, 5);
        assert!(!sim.alive);
        assert!(sim.death_branch);
        assert_eq!(sim.survival_ms, 1000);
        assert_eq!(sim.stamina_milli, 1000);
    }

    #[test]
    fn exhaustion_kills_and_rejects_time_travel() {
        let mut sim = Sim::new(7);
        assert_eq!(sim.advance_idle(100_000), EV_DIED_EXHAUSTION);
        assert!(!sim.alive);
        assert_eq!(sim_death_of(&sim), 2);
        assert_eq!(sim.chop(SIDE_LEFT, 200_000), EV_ALREADY_DEAD);
        let mut sim2 = Sim::new(7);
        sim2.chop(SIDE_LEFT, 500);
        assert_eq!(sim2.chop(SIDE_LEFT, 100), EV_INVALID_TIME);
    }

    fn sim_death_of(sim: &Sim) -> u32 {
        if sim.alive {
            0
        } else if sim.death_branch {
            1
        } else {
            2
        }
    }

    #[test]
    fn rejuvenation_cycle_is_timer_driven() {
        // Chop NONE-side-safe inputs is hard; instead idle in young phase is
        // impossible (idle drains). Drive 31 s of safe play is impractical
        // here — assert the timers directly through repeated small advances
        // with a death-free seed by chopping the safe side each time.
        let mut sim = Sim::new(2026);
        let mut t = 0u32;
        let mut user_side = SIDE_LEFT;
        // Mirror what the game does: always chop away from the bottom branch.
        for _ in 0..200 {
            t += 150;
            let bottom = sim.segments[0];
            user_side = if bottom == SIDE_LEFT {
                SIDE_RIGHT
            } else {
                SIDE_LEFT
            };
            let ev = sim.chop(user_side, t);
            if ev != EV_ALIVE {
                break;
            }
            if sim.rejuvenations > 0 {
                break;
            }
        }
        assert!(
            sim.rejuvenations > 0,
            "should rejuvenate within 30 s of play"
        );
        assert!(sim.phase_young || !sim.alive);
    }
}
