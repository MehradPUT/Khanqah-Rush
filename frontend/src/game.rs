//! Round state machine: the reference sim plus presentation state.
//!
//! Phase 3 plays Nima (hero select lands with the DOM carousel in
//! Phase 4). Seeds are time-based; server URLs carry official seeds in
//! Phase 5 with the companion integration.
//!
//! Faithfulness note (verified against the bundle): the lumberjack body
//! never moves or swaps on normal chops — `m` changes only via `wa()`,
//! which Nima rounds never call, and swing textures only play on
//! shield/flame absorbs. The tree, chips, score, and stamina bar carry
//! all chop feedback.

use khanqah_sim::{Sim, SIDE_LEFT, SIDE_RIGHT};
use std::time::{SystemTime, UNIX_EPOCH};

pub struct Game {
    pub sim: Sim,
}

impl Game {
    pub fn new_round() -> Self {
        let seed = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_nanos() as u64)
            .unwrap_or(0x1234_5678);
        Self {
            sim: Sim::new(seed),
        }
    }

    /// Player chop; returns the sim event code.
    pub fn chop(&mut self, left: bool, now_ms: u32) -> u32 {
        self.sim.chop(
            if left { SIDE_LEFT } else { SIDE_RIGHT },
            now_ms,
        )
    }

    pub fn alive(&self) -> bool {
        self.sim.alive
    }

    pub fn score(&self) -> u32 {
        self.sim.score
    }
}
