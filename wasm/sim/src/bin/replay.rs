//! Native replayer for the deterministic sim: proves host-side behavior
//! and generates golden vectors for the WASM cross-check tests.
//!
//! Usage: replay <seed> <SIDE@t_ms,...> <end_t_ms>
//!   SIDE is L or R. Example: replay 42 L@200,R@400,L@600 5000
//!
//! Prints: score=.. survival_ms=.. alive=.. death=.. stamina_left_ms=..

use khanqah_sim::{Sim, SIDE_LEFT, SIDE_RIGHT};
use std::env;

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 3 {
        eprintln!("usage: replay <seed> <SIDE@t_ms,...> <end_t_ms>");
        std::process::exit(2);
    }
    let seed: u64 = args[0].parse().expect("seed must be u64");
    let end_t: u32 = args[2].parse().expect("end_t_ms must be u32");

    let mut sim = Sim::new(seed);
    for chop in args[1].split(',') {
        let (side, t) = chop.split_once('@').expect("chop must look like L@200");
        let side = match side {
            "L" => SIDE_LEFT,
            "R" => SIDE_RIGHT,
            _ => panic!("side must be L or R"),
        };
        let t_ms: u32 = t.parse().expect("t_ms must be u32");
        let ev = sim.chop(side, t_ms);
        if ev != khanqah_sim::EV_ALIVE {
            break;
        }
    }
    if sim.alive {
        sim.advance_idle(end_t);
    }
    let death = if sim.alive {
        "none"
    } else if sim.death_branch {
        "branch"
    } else {
        "exhaustion"
    };
    println!(
        "score={} survival_ms={} alive={} death={} stamina_left_ms={}",
        sim.score,
        sim.survival_ms,
        sim.alive,
        death,
        sim.stamina_left_ms()
    );
}
