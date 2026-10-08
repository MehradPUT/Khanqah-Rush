//! Khanqah Rush deterministic simulation core — legacy-bundle mechanics.
//!
//! Integer game logic shared bit-identically by the reference (this Rust
//! core) and the server replay path (pure-JS port in shared/sim.js; the
//! Workers edge V8 refuses to compile WASM). No wall clock, no
//! allocator: outcomes are a pure function of `(hero, seed, inputs)`.
//!
//! Ported from the legacy bundle (`docs/bundle-map.md`):
//! - segment queue of side+magnitude entries (`-1/-2` LEFT, `1/2` RIGHT,
//!   `0` none), spawned in pairs off a single 50/50 draw;
//! - chop shifts one entry, replenishes a pair when the queue is odd;
//! - lethal chop = branch on the player's side (score NOT incremented);
//! - stamina is a *deadline* timestamp: first chop sets `t+4250`, each
//!   survived chop adds 250 ms capped at `t+8500`; the frame loop kills
//!   past the deadline (chops themselves never check it — a late chop
//!   while still alive is processed, then the round is already over;
//!   the sim kills before processing, an accepted sub-frame residual);
//! - score increments only on survived chops.
//!
//! Hero models (all eight, positive-evidence reversed from Ca/Va/Ta):
//! - Nima: 20 s rejuvenation cycle, deadline pinned past 15 s.
//! - Fargol: 100 non-flame chops start a 5 s flame (stamina pinned,
//!   lethal branches survive with +1); one Parsa sacrifice survives a
//!   lethal/exhaustion with an 880 ms input blackout and a cleanup
//!   shift +1 at ~420 ms.
//! - Ali: every 50 counted chops trigger 10 auto safe chops at 95 ms
//!   cadence (stamina pinned, manual inputs ignored); counter never
//!   resets.
//! - Ahmad: every 100 chops earns a stacking shield; a shield absorbs a
//!   lethal (+1, extra shift) or an exhaustion (cleanup shift +1).
//! - Parsa: exhaustion with blankets left naps (3 s sleep + indefinite
//!   wait, both stamina-pinned) instead of dying, up to twice; the next
//!   chop resumes full.
//! - Amirhossein: +1 extra per survived chop. Erfan: +2 extra when
//!   post-chop stamina is below half. Fateme: base mechanics.
//! - Levels: every `ca % 20 === 0` after an increment shrinks the
//!   stamina window and refill (`qa/ga *= 0.95`, float64 chain — the
//!   exact op order is the cross-engine contract).
//!
//! Determinism contract: f64 is used for stamina deadlines so the
//! float64 difficulty chain matches the bundle bit-for-bit. Same
//! IEEE754 ops in the same order stay identical across Rust, WASM,
//! and JS engines. Round clocks stay far below 2^31 ms, where integer
//! timestamps convert exactly.

pub const SIM_VERSION: u32 = 2;
pub const QUEUE_CAP: usize = 16;

pub const SIDE_NONE: i8 = 0;
pub const SIDE_LEFT: i8 = 1;
pub const SIDE_RIGHT: i8 = 2;

// Hero ids (trace v2, shared/trace-codec.js single source).
pub const HERO_NIMA: u8 = 0;
pub const HERO_FARGOL: u8 = 1;
pub const HERO_ALI: u8 = 2;
pub const HERO_AMIRHOSSEIN: u8 = 3;
pub const HERO_PARSA: u8 = 4;
pub const HERO_AHMAD: u8 = 5;
pub const HERO_ERFAN: u8 = 6;
pub const HERO_FATEME: u8 = 7;

// Nima rejuvenation: 20 s cycle, stamina pinned full while
// cycle position >= 15 s (legacy `ba = now + qa` every frame there).
const REJUV_CYCLE_MS: u32 = 20_000;
const REJUV_FROM_MS: u32 = 15_000;
const REJUV_WINDOW_MS: u32 = REJUV_CYCLE_MS - REJUV_FROM_MS;

// Event codes returned by chop/advance.
pub const EV_ALIVE: u32 = 0;
pub const EV_DIED_BRANCH: u32 = 1;
pub const EV_DIED_EXHAUSTION: u32 = 2;
pub const EV_INVALID_TIME: u32 = 3;
pub const EV_ALREADY_DEAD: u32 = 4;

const FIRST_GRACE_MS: f64 = 4250.0;
const QA_MS: f64 = 8500.0;
const GA_MS: f64 = 250.0;

// Ability tuning, all positive-evidence from the bundle.
const FLAME_MS: u32 = 5000;
const FARGOL_FLAME_EVERY: u32 = 100;
const SACRIFICE_MS: u32 = 880;
const SACRIFICE_IMPACT_MS: u32 = 420;
const FLURRY_COUNT: u32 = 10;
const FLURRY_STEP_MS: u32 = 95;
const ALI_FLURRY_EVERY: u32 = 50;
const AHMAD_SHIELD_EVERY: u32 = 100;
const PARSA_NAPS: u32 = 2;
const PARSA_SLEEP_MS: u32 = 3000;

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

fn in_rejuv_window(t_ms: u32) -> bool {
    t_ms % REJUV_CYCLE_MS >= REJUV_FROM_MS
}

/// End (exclusive) of the rejuvenation window containing `t_ms`.
fn rejuv_window_exit(t_ms: u32) -> u32 {
    t_ms - t_ms % REJUV_CYCLE_MS + REJUV_CYCLE_MS
}

/// Start of the first rejuvenation window strictly after `t_ms`.
/// None only on u32 overflow (round clocks never get there).
fn first_rejuv_start_after(t_ms: u32) -> Option<u32> {
    let k = if t_ms < REJUV_FROM_MS {
        0u64
    } else {
        (t_ms - REJUV_FROM_MS) as u64 / REJUV_CYCLE_MS as u64 + 1
    };
    let start = k * REJUV_CYCLE_MS as u64 + REJUV_FROM_MS as u64;
    if start > u32::MAX as u64 {
        None
    } else {
        Some(start as u32)
    }
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Sim {
    rng: u64,
    pub score: u32,
    pub deadline_ms: f64,
    pub started: bool,
    pub survival_ms: u64,
    pub alive: bool,
    pub death_branch: bool,
    pub last_t_ms: u32,
    pub queue: [i8; QUEUE_CAP],
    pub queue_len: usize,
    pub hero: u8,
    pub rejuvenations: u32,
    entered_rejuv: bool,
    pub qa_ms: f64,
    pub ga_ms: f64,
    pub hero_chops: u32,
    pub player_left: bool,
    pub flame_start_ms: Option<u32>,
    pub sacrifice_used: bool,
    pub sacrifice_ignore_until_ms: u32,
    pub sacrifice_impact_at_ms: Option<u32>,
    pub sacrifice_impact_left: bool,
    pub flurry_active: bool,
    pub flurry_remaining: u32,
    pub flurry_next_at_ms: u32,
    pub shields: u32,
    pub sleeps_used: u32,
    pub nap_start_ms: u32,
    pub suspended: bool,
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
            hero: HERO_NIMA,
            rejuvenations: 0,
            entered_rejuv: false,
            qa_ms: QA_MS,
            ga_ms: GA_MS,
            hero_chops: 0,
            player_left: false,
            flame_start_ms: None,
            sacrifice_used: false,
            sacrifice_ignore_until_ms: 0,
            sacrifice_impact_at_ms: None,
            sacrifice_impact_left: false,
            flurry_active: false,
            flurry_remaining: 0,
            flurry_next_at_ms: 0,
            shields: 0,
            sleeps_used: 0,
            nap_start_ms: 0,
            suspended: false,
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

    /// One queue shift with odd-length replenish (bundle `$a` without the
    /// visuals). Consumes one RNG draw exactly when the queue is odd.
    fn shift_entry(&mut self) -> i8 {
        if self.queue_len % 2 == 1 {
            self.push_pair();
        }
        self.shift()
    }

    /// Shatter a `|x| === 1` branch: same shift, no score.
    fn shatter_if_small(&mut self) {
        if self.queue_len > 0 && self.queue[0].abs() == 1 {
            self.shift_entry();
        }
    }

    fn collides(left: bool, bottom: i8) -> bool {
        left == (bottom < 0)
    }

    /// Branch-cleanup pattern shared by the sacrifice impact and the
    /// Ahmad exhaustion save: shatter, then shift + score when the (new)
    /// bottom still collides. NOTE: the bundle omits the nonzero guard
    /// on the re-check, so a NONE bottom "collides" for RIGHT-side play.
    fn cleanup_collide(&mut self) {
        if self.queue_len > 0 {
            let b = self.queue[0];
            if b != SIDE_NONE && Self::collides(self.player_left, b) && b.abs() == 1 {
                self.shift_entry();
            }
        }
        if self.queue_len > 0 {
            let b = self.queue[0];
            if Self::collides(self.player_left, b) {
                self.shift_entry();
                self.score_point();
            }
        }
    }

    /// One score point plus the difficulty ramp: every `ca % 20 === 0`
    /// shrinks the stamina window and refill (`nb()`, float64 chain).
    fn score_point(&mut self) {
        self.score += 1;
        if self.score % 20 == 0 {
            self.qa_ms *= 0.95;
            self.ga_ms *= 0.95;
        }
    }

    /// Erfan's +2 lands as one block with a single post-check.
    fn score_bonus2(&mut self) {
        self.score += 2;
        if self.score % 20 == 0 {
            self.qa_ms *= 0.95;
            self.ga_ms *= 0.95;
        }
    }

    fn refill(&mut self, t_ms: u32) {
        let t = t_ms as f64;
        self.deadline_ms = (self.deadline_ms + self.ga_ms).min(t + self.qa_ms);
    }

    fn pin_full(&mut self, t_ms: u32) {
        self.deadline_ms = t_ms as f64 + self.qa_ms;
    }

    fn flame_active_at(&self, t_ms: u32) -> bool {
        match self.flame_start_ms {
            Some(s) => t_ms.saturating_sub(s) < FLAME_MS,
            None => false,
        }
    }

    /// Ali's safe side: first nonzero of the bottom three, else player.
    fn ali_safe_side(&self) -> bool {
        for i in 0..3 {
            if i < self.queue_len && self.queue[i] != SIDE_NONE {
                return self.queue[i] > 0;
            }
        }
        self.player_left
    }

    /// Run pending flurry auto-chops scheduled at or below `upto_ms`.
    /// Each is a base chop on the safe side (score, refill, stamina
    /// pin) with no counter progress and no retrigger.
    fn flush_flurry(&mut self, upto_ms: u32) {
        while self.alive && self.flurry_active && self.flurry_next_at_ms <= upto_ms {
            let t = self.flurry_next_at_ms;
            let safe_left = self.ali_safe_side();
            self.shift_entry();
            self.score_point();
            self.pin_full(t);
            self.player_left = self.ali_safe_side();
            let _ = safe_left;
            self.flurry_remaining -= 1;
            self.flurry_next_at_ms = self.flurry_next_at_ms.saturating_add(FLURRY_STEP_MS);
            if self.flurry_remaining == 0 {
                self.flurry_active = false;
            }
        }
    }

    /// Per-hero progress that runs on EVERY chop reaching Ca's tail —
    /// including lethal ones (the bundle falls through into the per-hero
    /// blocks after `Va()`). Scoring here is on top of the base chop:
    /// Amirhossein +1 and Erfan clutch +2 apply even on death chops.
    fn hero_progress(&mut self, t_ms: u32) {
        match self.hero {
            HERO_FARGOL if !self.flame_active_at(t_ms) => {
                self.hero_chops += 1;
                if self.hero_chops > 0 && self.hero_chops % FARGOL_FLAME_EVERY == 0 {
                    self.flame_start_ms = Some(t_ms);
                }
            }
            HERO_ALI if !self.flurry_active => {
                self.hero_chops += 1;
                if self.hero_chops > 0 && self.hero_chops % ALI_FLURRY_EVERY == 0 {
                    self.flurry_active = true;
                    self.flurry_remaining = FLURRY_COUNT;
                    self.flurry_next_at_ms = t_ms.saturating_add(FLURRY_STEP_MS);
                    self.pin_full(t_ms);
                    self.player_left = self.ali_safe_side();
                }
            }
            HERO_AMIRHOSSEIN => {
                self.score_point();
            }
            HERO_ERFAN => {
                if (self.deadline_ms - t_ms as f64) / self.qa_ms < 0.5 {
                    self.score_bonus2();
                }
            }
            HERO_AHMAD => {
                self.hero_chops += 1;
                if self.hero_chops > 0 && self.hero_chops % AHMAD_SHIELD_EVERY == 0 {
                    self.shields += 1;
                }
            }
            _ => {}
        }
    }

    /// Sacrifice impact + Ahmad exhaustion cleanup share the pattern;
    /// applied once when the clock crosses the impact time.
    fn maybe_impact(&mut self, t_ms: u32) {
        if let Some(at) = self.sacrifice_impact_at_ms {
            if at <= t_ms {
                self.sacrifice_impact_at_ms = None;
                self.cleanup_collide();
            }
        }
    }

    /// Stamina deadline (legacy `ba`): the initial grace counts from
    /// round start even before the first chop refreshes it.
    /// Nima rejuvenation: while the 20 s cycle sits at >= 15 s, legacy
    /// pins the deadline to now + full window every frame. A jump that
    /// lands inside or past a window must credit pinning for the
    /// crossed span, not just the landing position: reaching a window
    /// alive carries the round through it (deadline tracks ahead of
    /// the clock the whole time). At most one fresh window can extend
    /// survival per advance — pinning through a full window sets
    /// deadline = exit + qa, which always precedes the next start.
    fn advance_clock(&mut self, t_ms: u32) {
        self.survival_ms = self.survival_ms.max(t_ms as u64);
        let prev = self.last_t_ms;
        self.last_t_ms = prev.max(t_ms);
        if self.hero != HERO_NIMA {
            self.entered_rejuv = false;
            return;
        }
        let was_in = in_rejuv_window(prev);
        let now_in = in_rejuv_window(t_ms);
        if was_in {
            let exit = rejuv_window_exit(prev);
            let pinned = t_ms.min(exit) as f64 + self.qa_ms;
            if pinned > self.deadline_ms {
                self.deadline_ms = pinned;
            }
            if !self.entered_rejuv {
                self.rejuvenations += 1;
            }
        } else if let Some(start) = first_rejuv_start_after(prev) {
            if start <= t_ms && (start as f64) <= self.deadline_ms {
                let exit = start.saturating_add(REJUV_WINDOW_MS);
                self.deadline_ms = t_ms.min(exit) as f64 + self.qa_ms;
                self.rejuvenations += 1;
            }
        }
        self.entered_rejuv = now_in;
    }

    /// Exhaustion gate at time `t_ms`. Returns true when the round dies.
    /// Parsa naps (up to twice) and Ahmad/Fargol saves apply exactly as
    /// the frame-loop `Va()` would have fired them.
    fn check_exhaustion(&mut self, t_ms: u32) -> bool {
        if self.suspended || (t_ms as f64) <= self.deadline_ms {
            return false;
        }
        // Anchor save windows at the pre-update deadline: the frame loop
        // would have fired there, not at the late event time.
        let anchor = self.deadline_ms;
        if self.hero == HERO_PARSA && self.sleeps_used < PARSA_NAPS {
            self.sleeps_used += 1;
            self.suspended = true;
            self.nap_start_ms = anchor as u32;
            self.pin_full(t_ms);
            return false;
        }
        if self.hero == HERO_AHMAD && self.shields > 0 {
            self.shields -= 1;
            self.pin_full(t_ms);
            self.cleanup_collide();
            return false;
        }
        if self.hero == HERO_FARGOL && !self.sacrifice_used {
            self.sacrifice_used = true;
            self.pin_full(t_ms);
            self.sacrifice_ignore_until_ms = (anchor as u32).saturating_add(SACRIFICE_MS);
            self.sacrifice_impact_at_ms = Some((anchor as u32).saturating_add(SACRIFICE_IMPACT_MS));
            self.sacrifice_impact_left = self.player_left;
            return false;
        }
        self.alive = false;
        self.death_branch = false;
        true
    }

    /// Continuous stamina pins the frame loop applies between events:
    /// flame heat and the sacrifice cinematic track now + qa every
    /// frame. (Flurry pins per auto-chop instead; naps suspend the
    /// check outright; Nima pinning lives in advance_clock.)
    fn apply_pins(&mut self, t_ms: u32) {
        let pinned = t_ms as f64 + self.qa_ms;
        if self.hero == HERO_FARGOL
            && (self.flame_active_at(t_ms) || t_ms < self.sacrifice_ignore_until_ms)
            && pinned > self.deadline_ms
        {
            self.deadline_ms = pinned;
        }
    }

    /// Apply a chop. Returns an EV_* code.
    /// `side`: SIDE_LEFT or SIDE_RIGHT (C ABI: 1 = LEFT, anything else
    /// is RIGHT — the bundle never sends anything else).
    pub fn chop(&mut self, side: i8, t_ms: u32) -> u32 {
        if !self.alive {
            return EV_ALREADY_DEAD;
        }
        if t_ms < self.last_t_ms {
            return EV_INVALID_TIME;
        }
        let left = side == SIDE_LEFT;
        // Flurry autos at or below now go first: strict time order.
        self.flush_flurry(t_ms);
        if !self.alive {
            return EV_ALREADY_DEAD;
        }
        // Time-driven effects land before input handling.
        self.maybe_impact(t_ms);
        self.apply_pins(t_ms);
        // Sacrifice cinematic: inputs ignored (companion gates these;
        // the window covers stale clients and boundary races).
        if self.hero == HERO_FARGOL && t_ms < self.sacrifice_ignore_until_ms {
            return EV_ALIVE;
        }
        // Ali manual chops during flurry are ignored outright.
        if self.hero == HERO_ALI && self.flurry_active {
            return EV_ALIVE;
        }
        if !self.started {
            self.started = true;
            self.deadline_ms = t_ms as f64 + FIRST_GRACE_MS;
        }
        // Parsa wake: a chop while waiting resumes with full stamina.
        // A chop still inside the 3 s sleep is ignored instead.
        if self.suspended {
            if t_ms < self.nap_start_ms.saturating_add(PARSA_SLEEP_MS) {
                return EV_ALIVE;
            }
            self.suspended = false;
            self.pin_full(t_ms);
        }
        self.advance_clock(t_ms);
        // Exhaustion at chop time: the frame loop would have fired
        // first, so saves apply without processing — except the Ahmad
        // shield save, whose cleanup already ran, letting the chop
        // through normally. Anchors use the pre-update deadline as the
        // Va-time proxy.
        if (t_ms as f64) > self.deadline_ms {
            let anchor = self.deadline_ms;
            if self.hero == HERO_PARSA && self.sleeps_used < PARSA_NAPS {
                self.sleeps_used += 1;
                self.nap_start_ms = anchor as u32;
                self.pin_full(t_ms);
                if t_ms < (anchor as u32).saturating_add(PARSA_SLEEP_MS) {
                    self.suspended = true;
                    return EV_ALIVE;
                }
            } else if self.hero == HERO_AHMAD && self.shields > 0 {
                self.shields -= 1;
                self.pin_full(t_ms);
                self.cleanup_collide();
            } else if self.hero == HERO_FARGOL && !self.sacrifice_used {
                self.sacrifice_used = true;
                self.pin_full(t_ms);
                self.sacrifice_ignore_until_ms =
                    (anchor as u32).saturating_add(SACRIFICE_MS);
                self.sacrifice_impact_at_ms =
                    Some((anchor as u32).saturating_add(SACRIFICE_IMPACT_MS));
                self.sacrifice_impact_left = self.player_left;
                return EV_ALIVE;
            } else {
                self.alive = false;
                self.death_branch = false;
                return EV_DIED_EXHAUSTION;
            }
        }
        // Ahmad shield intercept: absorb a lethal branch (+1, extra
        // shift). Blocked chops don't advance the earn counter.
        if self.hero == HERO_AHMAD && self.shields > 0 {
            let bottom = if self.queue_len > 0 {
                self.queue[0]
            } else {
                SIDE_NONE
            };
            if bottom != SIDE_NONE && Self::collides(left, bottom) {
                self.shatter_if_small();
                self.shields -= 1;
                self.pin_full(t_ms);
                self.score_point();
                self.shift_entry();
                self.player_left = left;
                return EV_ALIVE;
            }
        }
        // Fargol flame intercept: lethal branches survive with +1.
        if self.hero == HERO_FARGOL && self.flame_active_at(t_ms) {
            let bottom = if self.queue_len > 0 {
                self.queue[0]
            } else {
                SIDE_NONE
            };
            if bottom != SIDE_NONE && Self::collides(left, bottom) {
                self.shatter_if_small();
                self.pin_full(t_ms);
                self.score_point();
                self.shift_entry();
                self.player_left = left;
                return EV_ALIVE;
            }
        }
        // Normal branch check: a lethal shatters `|x| === 1` and shifts
        // nothing otherwise. Post-death queue state only matters via
        // survival saves, which manage their own shifts — so unlike a
        // survived chop there is no unconditional shift here.
        let bottom = if self.queue_len > 0 {
            self.queue[0]
        } else {
            SIDE_NONE
        };
        if bottom != SIDE_NONE && Self::collides(left, bottom) {
            self.shatter_if_small();
            if self.hero == HERO_FARGOL && !self.sacrifice_used {
                // Va() sacrifice: survive, cinematic blackout, cleanup at
                // impact. The trigger chop itself scores nothing.
                self.sacrifice_used = true;
                self.pin_full(t_ms);
                self.sacrifice_ignore_until_ms = t_ms.saturating_add(SACRIFICE_MS);
                self.sacrifice_impact_at_ms =
                    Some(t_ms.saturating_add(SACRIFICE_IMPACT_MS));
                self.sacrifice_impact_left = self.player_left;
                self.hero_progress(t_ms);
                return EV_ALIVE;
            }
            self.alive = false;
            self.death_branch = true;
            // Falls through into the per-hero blocks even on death.
            self.hero_progress(t_ms);
            return EV_DIED_BRANCH;
        }
        // Survived chop: exactly one shift, then refill BEFORE scoring —
        // the bundle refills `ba` before the `ca++` level check.
        // NOTE: no `wa()` runs here, so the player side is untouched.
        self.shift_entry();
        self.refill(t_ms);
        self.score_point();
        self.hero_progress(t_ms);
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
        self.flush_flurry(t_ms);
        if !self.alive {
            return EV_ALREADY_DEAD;
        }
        self.maybe_impact(t_ms);
        self.advance_clock(t_ms);
        self.apply_pins(t_ms);
        if self.suspended {
            return EV_ALIVE;
        }
        if self.check_exhaustion(t_ms) {
            self.advance_clock(t_ms);
            return EV_DIED_EXHAUSTION;
        }
        EV_ALIVE
    }

    /// Milliseconds of stamina left at the current clock.
    pub fn stamina_left_ms(&self) -> u32 {
        if !self.alive {
            return 0;
        }
        (self.deadline_ms - self.last_t_ms as f64).max(0.0) as u32
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

/// Select the hero model. 0 = Nima … 7 = Fateme (trace v2 ids);
/// anything else runs base mechanics.
#[no_mangle]
pub extern "C" fn sim_set_character(id: u8) {
    game_mut().hero = id;
}

/// Legacy has no old/young phase counter apart from rejuvenation count;
/// kept for ABI stability, always 0.
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

    /// Chop the safe side of whatever sits at the queue bottom.
    fn chop_safe(sim: &mut Sim, t_ms: u32) -> u32 {
        let side = if sim.queue[0] < 0 { SIDE_RIGHT } else { SIDE_LEFT };
        sim.chop(side, t_ms)
    }

    #[test]
    fn nima_rejuvenation_bridges_idle_past_deadline() {
        // Keep chopping into the first window, then go idle past what the
        // plain deadline would allow. Nima pins through the window and
        // lives; ability-free Fateme dies of exhaustion on the same inputs.
        let mut nima = Sim::new(42);
        let mut t = 0u32;
        for _ in 0..100 {
            t += 150;
            assert_eq!(chop_safe(&mut nima, t), EV_ALIVE);
        }
        assert_eq!(t, 15_000);
        assert_eq!(nima.rejuvenations, 1);
        assert_eq!(nima.advance_idle(24_000), EV_ALIVE);
        assert!(nima.alive);

        let mut other = Sim::new(42);
        other.hero = HERO_FATEME;
        let mut t = 0u32;
        for _ in 0..100 {
            t += 150;
            assert_eq!(chop_safe(&mut other, t), EV_ALIVE);
        }
        assert_eq!(other.rejuvenations, 0);
        assert_eq!(other.advance_idle(24_000), EV_DIED_EXHAUSTION);
        assert!(!other.alive);
        assert!(!other.death_branch);
    }

    #[test]
    fn rejuvenation_counts_one_per_window() {
        // Safe-side play straight through two windows counts each entry
        // once and never dies of exhaustion mid-window.
        let mut sim = Sim::new(7);
        let mut t = 0u32;
        for _ in 0..250 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(t, 37_500);
        assert!(sim.alive);
        assert_eq!(sim.rejuvenations, 2);
    }

    #[test]
    fn dead_window_entry_does_not_pin() {
        // Reaching a window already past the deadline still kills: a
        // fresh round idling from the start never survives to 15 s.
        let mut sim = Sim::new(7);
        assert_eq!(sim.advance_idle(16_000), EV_DIED_EXHAUSTION);
        assert_eq!(sim.rejuvenations, 0);
    }

    /// Chop into whatever the bottom branch faces (forcing a lethal
    /// when it is nonzero). Returns the event code.
    fn force_lethal(sim: &mut Sim, t_ms: &mut u32) -> u32 {
        for _ in 0..24 {
            let bottom = sim.queue[0];
            *t_ms += 150;
            if bottom == SIDE_NONE {
                let ev = chop_safe(sim, *t_ms);
                assert_eq!(ev, EV_ALIVE);
                continue;
            }
            let side = if bottom < 0 { SIDE_LEFT } else { SIDE_RIGHT };
            return sim.chop(side, *t_ms);
        }
        panic!("no branch found within 24 chops");
    }

    #[test]
    fn fargol_flame_blocks_lethal_with_bonus() {
        // 100 counted chops light the flame; a lethal inside it
        // survives with +1 instead of dying.
        let mut sim = Sim::new(42);
        sim.hero = HERO_FARGOL;
        let mut t = 0u32;
        for _ in 0..100 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(sim.score, 100);
        assert!(sim.flame_active_at(t));
        assert_eq!(force_lethal(&mut sim, &mut t), EV_ALIVE);
        assert!(sim.alive);
        assert_eq!(sim.score, 101);
        assert!(!sim.sacrifice_used);
    }

    #[test]
    fn fargol_sacrifice_survives_once_with_cleanup() {
        // Lethal outside flame: survive via sacrifice, cleanup shift +1
        // lands at impact, and the next lethal kills.
        let mut found = None;
        for seed in 0..1000u64 {
            let mut sim = Sim::new(seed);
            sim.hero = HERO_FARGOL;
            sim.chop(SIDE_LEFT, 100);
            sim.chop(SIDE_LEFT, 200);
            if sim.queue[0] < 0 {
                found = Some(seed);
                break;
            }
        }
        let mut sim = Sim::new(found.expect("lethal seed"));
        sim.hero = HERO_FARGOL;
        assert_eq!(sim.chop(SIDE_LEFT, 100), EV_ALIVE);
        assert_eq!(sim.chop(SIDE_LEFT, 200), EV_ALIVE);
        assert_eq!(sim.chop(SIDE_LEFT, 300), EV_ALIVE);
        assert!(sim.alive);
        assert!(sim.sacrifice_used);
        assert_eq!(sim.score, 2);
        // Impact cleanup (+0/+1) applies on the next advance past +420.
        assert_eq!(sim.advance_idle(720), EV_ALIVE);
        assert!(sim.score == 2 || sim.score == 3);
        // Inputs inside the 880 ms blackout are swallowed.
        assert_eq!(sim.chop(SIDE_LEFT, 800), EV_ALIVE);
        assert!(sim.score == 2 || sim.score == 3);
        // Past the blackout a fresh lethal kills (sacrifice spent).
        let mut t = 2000u32;
        assert_eq!(force_lethal(&mut sim, &mut t), EV_DIED_BRANCH);
        assert!(!sim.alive);
    }

    #[test]
    fn ali_flurry_autos_score_ten() {
        // 50 counted chops trigger 10 auto safe chops at 95 ms cadence.
        let mut sim = Sim::new(42);
        sim.hero = HERO_ALI;
        let mut t = 0u32;
        for _ in 0..50 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(sim.score, 50);
        assert!(sim.flurry_active);
        assert_eq!(sim.flurry_remaining, 10);
        assert_eq!(sim.advance_idle(t + 950), EV_ALIVE);
        assert!(!sim.flurry_active);
        assert_eq!(sim.score, 60);
        assert!(sim.alive);
    }

    #[test]
    fn ahmad_shield_earns_and_absorbs() {
        // 100 chops earn one shield; it absorbs a lethal with +1, then
        // the next lethal kills.
        let mut sim = Sim::new(42);
        sim.hero = HERO_AHMAD;
        let mut t = 0u32;
        for _ in 0..100 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(sim.score, 100);
        assert_eq!(sim.shields, 1);
        assert_eq!(force_lethal(&mut sim, &mut t), EV_ALIVE);
        assert!(sim.alive);
        assert_eq!(sim.shields, 0);
        assert_eq!(sim.score, 101);
        assert_eq!(force_lethal(&mut sim, &mut t), EV_DIED_BRANCH);
        assert!(!sim.alive);
    }

    #[test]
    fn ahmad_shield_saves_exhaustion() {
        let mut sim = Sim::new(42);
        sim.hero = HERO_AHMAD;
        let mut t = 0u32;
        for _ in 0..100 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(sim.shields, 1);
        assert_eq!(sim.advance_idle(100_000), EV_ALIVE);
        assert!(sim.alive);
        assert_eq!(sim.shields, 0);
    }

    #[test]
    fn parsa_nap_and_wake() {
        // Exhaustion with blankets left naps instead of dying; a chop
        // inside the 3 s sleep is swallowed, a later one wakes fully.
        let mut sim = Sim::new(7);
        sim.hero = HERO_PARSA;
        assert_eq!(sim.chop(SIDE_LEFT, 100), EV_ALIVE);
        assert_eq!(sim.score, 1);
        // Past the 4600 ms deadline: nap + ignore, score untouched.
        assert_eq!(sim.chop(SIDE_LEFT, 5000), EV_ALIVE);
        assert!(sim.alive);
        assert!(sim.suspended);
        assert_eq!(sim.sleeps_used, 1);
        assert_eq!(sim.score, 1);
        // Still inside nap_start + 3000: swallowed.
        assert_eq!(sim.chop(SIDE_LEFT, 6000), EV_ALIVE);
        assert_eq!(sim.score, 1);
        // Past the sleep: wake chop scores and resumes.
        assert_eq!(chop_safe(&mut sim, 15_000), EV_ALIVE);
        assert_eq!(sim.score, 2);
        assert!(!sim.suspended);
    }

    #[test]
    fn parsa_third_exhaustion_kills() {
        let mut sim = Sim::new(7);
        sim.hero = HERO_PARSA;
        assert_eq!(sim.chop(SIDE_LEFT, 100), EV_ALIVE);
        assert_eq!(sim.advance_idle(10_000), EV_ALIVE);
        assert_eq!(sim.sleeps_used, 1);
        // Wake, then exhaust twice more (second nap, then death).
        assert_eq!(chop_safe(&mut sim, 15_000), EV_ALIVE);
        assert_eq!(sim.advance_idle(30_000), EV_ALIVE);
        assert_eq!(sim.sleeps_used, 2);
        assert_eq!(chop_safe(&mut sim, 35_000), EV_ALIVE);
        assert_eq!(sim.advance_idle(60_000), EV_DIED_EXHAUSTION);
        assert!(!sim.alive);
    }

    #[test]
    fn amirhossein_doubles_score() {
        let mut sim = Sim::new(42);
        sim.hero = HERO_AMIRHOSSEIN;
        let mut t = 0u32;
        for _ in 0..5 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(sim.score, 10);
    }

    #[test]
    fn erfan_clutch_triples_when_tired() {
        // First chop at full stamina scores 1; a chop near exhaustion
        // scores 3 (1 + 2 clutch bonus).
        let mut sim = Sim::new(7);
        sim.hero = HERO_ERFAN;
        assert_eq!(sim.chop(SIDE_LEFT, 100), EV_ALIVE);
        assert_eq!(sim.score, 1);
        assert_eq!(sim.advance_idle(4400), EV_ALIVE);
        assert_eq!(chop_safe(&mut sim, 4400), EV_ALIVE);
        assert_eq!(sim.score, 4);
    }

    #[test]
    fn amirhossein_scores_on_death_chop() {
        // The per-hero block runs even after Va(): a lethal chop still
        // pays the multiplier point.
        let mut sim = Sim::new(7);
        sim.hero = HERO_AMIRHOSSEIN;
        assert_eq!(sim.chop(SIDE_LEFT, 100), EV_ALIVE);
        assert_eq!(sim.score, 2);
        sim.queue[0] = -1;
        assert_eq!(sim.chop(SIDE_LEFT, 200), EV_DIED_BRANCH);
        assert_eq!(sim.score, 3);
    }

    #[test]
    fn erfan_clutch_scores_on_death_chop() {
        let mut sim = Sim::new(7);
        sim.hero = HERO_ERFAN;
        assert_eq!(sim.chop(SIDE_LEFT, 100), EV_ALIVE);
        assert_eq!(sim.score, 1);
        sim.queue[0] = -1;
        sim.deadline_ms = 300.0;
        assert_eq!(sim.chop(SIDE_LEFT, 200), EV_DIED_BRANCH);
        assert_eq!(sim.score, 3);
    }

    #[test]
    fn levels_shrink_stamina_window() {
        // 20 base chops level once: qa/ga chain exactly one ×0.95 step.
        let mut sim = Sim::new(42);
        sim.hero = HERO_FATEME;
        let mut t = 0u32;
        for _ in 0..20 {
            t += 150;
            assert_eq!(chop_safe(&mut sim, t), EV_ALIVE);
        }
        assert_eq!(sim.score, 20);
        assert_eq!(sim.qa_ms, 8500.0 * 0.95);
        assert_eq!(sim.ga_ms, 250.0 * 0.95);
    }
}
