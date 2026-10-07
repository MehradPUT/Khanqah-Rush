//! Khanqah Rush deterministic simulation core — legacy-bundle mechanics.
//!
//! Integer-only game logic shared bit-identically by the browser (WASM) and
//! the server replay path (same artifact on Workers, native binary for local
//! checks). No floats, no wall clock, no allocator: outcomes are a pure
//! function of `(seed, inputs)`.
//!
//! Ported from the legacy bundle (`docs/bundle-map.md`):
//! - segment queue of side+magnitude entries (`-1/-2` LEFT, `1/2` RIGHT,
//!   `0` none), spawned in pairs off a single 50/50 draw;
//! - chop shifts one entry, replenishes a pair when the queue is odd;
//! - lethal chop = branch on the player's side (score NOT incremented);
//! - stamina is a *deadline* timestamp: first chop sets `t+4250`, each
//!   survived chop adds 250 ms capped at `t+8500`; passing the deadline
//!   without chopping kills by exhaustion.
//! - score increments only on survived chops.
//!
//! Character abilities are NOT modeled yet (follow-up): the core reports
//! raw outcomes; ability overrides arrive as declared inputs later.

pub const SIM_VERSION: u32 = 2;
pub const QUEUE_CAP: usize = 16;

pub const SIDE_NONE: i8 = 0;
pub const SIDE_LEFT: i8 = 1;
pub const SIDE_RIGHT: i8 = 2;

// Event codes returned by chop/advance.
pub const EV_ALIVE: u32 = 0;
pub const EV_DIED_BRANCH: u32 = 1;
pub const EV_DIED_EXHAUSTION: u32 = 2;
pub const EV_INVALID_TIME: u32 = 3;
pub const EV_ALREADY_DEAD: u32 = 4;

const FIRST_GRACE_MS: u32 = 4250;
const CHOP_REFILL_MS: u32 = 250;
const MAX_DEADLINE_AHEAD_MS: u32 = 8500;

fn splitmix64(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

/// One 50/50 draw, mirroring `500>=Math.floor(1E3*Math.random()+1)`.
fn coin_flip(rng: &mut u64) -> bool {
    ((splitmix64(rng) >> 32) as u32) < 0x8000_0000
}

fn branch_on(side: i8) -> bool {
    side < 0
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Sim {
    rng: u64,
    pub score: u32,
    pub deadline_ms: u32,
    pub started: bool,
    pub survival_ms: u64,
    pub alive: bool,
    pub death_branch: bool,
    pub last_t_ms: u32,
    pub queue: [i8; QUEUE_CAP],
    pub queue_len: usize,
}

impl Sim {
    pub fn new(seed: u64) -> Self {
        let mut sim = Self {
            rng: seed,
            score: 0,
            deadline_ms: FIRST_GRACE_MS,
            started: false,
            survival_ms: 0,
            alive: true,
            death_branch: false,
            last_t_ms: 0,
            queue: [SIDE_NONE; QUEUE_CAP],
            queue_len: 0,
        };
        // da=[0,0], then pairs while length < 11.
        sim.push_raw(SIDE_NONE);
        sim.push_raw(SIDE_NONE);
        while sim.queue_len < 11 {
            sim.push_pair();
        }
        sim
    }

    fn push_raw(&mut self, v: i8) {
        debug_assert!(self.queue_len < QUEUE_CAP);
        self.queue[self.queue_len] = v;
        self.queue_len += 1;
    }

    fn push_pair(&mut self) {
        let left = coin_flip(&mut self.rng);
        if left {
            self.push_raw(-1);
            self.push_raw(-2);
        } else {
            self.push_raw(1);
            self.push_raw(2);
        }
    }

    fn shift(&mut self) -> i8 {
        debug_assert!(self.queue_len > 0);
        let bottom = self.queue[0];
        self.queue.copy_within(1.., 0);
        self.queue_len -= 1;
        bottom
    }

    /// Advance the clock; returns true on exhaustion death.
    fn advance_to(&mut self, t_ms: u32) -> bool {
        self.survival_ms = self.survival_ms.max(t_ms as u64);
        self.last_t_ms = self.last_t_ms.max(t_ms);
        // Stamina deadline (legacy `ba`): the initial grace counts from
        // round start even before the first chop refreshes it.
        if self.alive && t_ms > self.deadline_ms {
            self.alive = false;
            self.death_branch = false;
            return true;
        }
        !self.alive
    }

    /// Apply a chop. Returns an EV_* code.
    pub fn chop(&mut self, side: i8, t_ms: u32) -> u32 {
        if !self.alive {
            return EV_ALREADY_DEAD;
        }
        if t_ms < self.last_t_ms {
            return EV_INVALID_TIME;
        }
        if !self.started {
            self.started = true;
            self.deadline_ms = t_ms.saturating_add(FIRST_GRACE_MS);
        }
        if self.advance_to(t_ms) {
            return EV_DIED_EXHAUSTION;
        }
        if self.queue_len % 2 == 1 {
            self.push_pair();
        }
        let bottom = self.shift();
        let hit = bottom != SIDE_NONE && ((side == SIDE_LEFT) == branch_on(bottom));
        if hit {
            self.alive = false;
            self.death_branch = true;
            return EV_DIED_BRANCH;
        }
        self.score += 1;
        self.deadline_ms = (self.deadline_ms + CHOP_REFILL_MS).min(t_ms + MAX_DEADLINE_AHEAD_MS);
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

    /// Milliseconds of stamina left at the current clock.
    pub fn stamina_left_ms(&self) -> u32 {
        if !self.alive {
            return 0;
        }
        self.deadline_ms.saturating_sub(self.last_t_ms)
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

/// Milliseconds of stamina left (0 when dead).
#[no_mangle]
pub extern "C" fn sim_stamina_milli() -> i32 {
    game_mut().stamina_left_ms() as i32
}

/// 0 = old phase model retired (legacy has no phases); always 0.
#[no_mangle]
pub extern "C" fn sim_phase() -> u32 {
    0
}

#[no_mangle]
pub extern "C" fn sim_survival_ms() -> u64 {
    game_mut().survival_ms
}

#[no_mangle]
pub extern "C" fn sim_rejuvenations() -> u32 {
    0
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
    game_mut().queue.as_ptr()
}

#[no_mangle]
pub extern "C" fn sim_segments_len() -> usize {
    game_mut().queue_len
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splitmix64_matches_published_vector() {
        // Steele, Lea & Flood (2014): seed 0 first yields 0xe220a8397b1dcdaf.
        let mut state = 0u64;
        assert_eq!(splitmix64(&mut state), 0xe220a8397b1dcdaf);
        assert_eq!(state, 0x9E37_79B9_7F4A_7C15);
    }

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

    /// Mirror of the bundle init: [0,0] then pairs while len < 11.
    fn expected_spawns(seed: u64, pairs: usize) -> Vec<i8> {
        let mut rng = seed;
        let mut out = vec![SIDE_NONE, SIDE_NONE];
        let mut len = 2;
        while len < 11 {
            if ((splitmix64(&mut rng) >> 32) as u32) < 0x8000_0000 {
                out.push(-1);
                out.push(-2);
            } else {
                out.push(1);
                out.push(2);
            }
            len += 2;
        }
        out.truncate(out.len().min(2 + pairs * 2));
        out
    }

    #[test]
    fn reset_layout_is_deterministic_and_bundle_shaped() {
        let a = Sim::new(12345);
        let b = Sim::new(12345);
        assert_eq!(a, b);
        assert_eq!(&a.queue[..2], &[SIDE_NONE, SIDE_NONE]);
        assert_eq!(a.queue_len, 12);
        assert_eq!(a.queue[..12], expected_spawns(12345, 5)[..]);
        assert_ne!(Sim::new(999).queue, a.queue);
    }

    #[test]
    fn golden_run_matches_recorded_values() {
        // Alternating sides every 200 ms on seed 42, verified against the
        // replay CLI. The vitest suite asserts the same numbers against
        // the compiled WASM build.
        let sides = [SIDE_LEFT, SIDE_RIGHT];
        let mut pattern = Vec::new();
        for i in 0..60 {
            pattern.push(sides[i % 2]);
        }
        let sim = play(42, &pattern, 200);
        assert_eq!(sim.score, 3);
        assert!(!sim.alive);
        assert!(sim.death_branch);
    }

    #[test]
    fn exhaustion_kills_and_rejects_time_travel() {
        let mut sim = Sim::new(7);
        // No chops: initial 4250 ms grace expires.
        assert_eq!(sim.advance_idle(100_000), EV_DIED_EXHAUSTION);
        assert!(!sim.alive);
        assert!(!sim.death_branch);
        assert_eq!(sim.chop(SIDE_LEFT, 200_000), EV_ALREADY_DEAD);
        let mut sim2 = Sim::new(7);
        sim2.chop(SIDE_LEFT, 500);
        assert_eq!(sim2.chop(SIDE_LEFT, 100), EV_INVALID_TIME);
    }

    #[test]
    fn lethal_chop_scores_nothing() {
        // The first two queue entries are always safe NONE; after two
        // safe chops the bottom is the first generated pair entry.
        let mut found = None;
        for seed in 0..1000u64 {
            let mut sim = Sim::new(seed);
            sim.chop(SIDE_LEFT, 100);
            sim.chop(SIDE_LEFT, 200);
            if sim.queue[0] < 0 {
                found = Some(seed);
                break;
            }
        }
        let seed = found.expect("a LEFT-facing third entry within 1000 seeds");
        let mut sim = Sim::new(seed);
        sim.chop(SIDE_LEFT, 100);
        sim.chop(SIDE_LEFT, 200);
        assert_eq!(sim.chop(SIDE_LEFT, 300), EV_DIED_BRANCH);
        assert_eq!(sim.score, 2);
    }
}
