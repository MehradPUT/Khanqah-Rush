//! Khanqah Rush frontend: Raylib + Rust, compiled to WASM.
//!
//! Phase 1 spike: open a window and draw. Later phases port the full
//! PIXI scene (tree, lumberjack, HUD, carousel, result screen) with
//! pixel parity, reusing `shared/sim.js` mechanics through a Rust port.

use raylib::prelude::*;

fn main() {
    let (mut rl, thread) = raylib::init().size(640, 480).title("Khanqah Rush").build();

    while !rl.window_should_close() {
        let mut d = rl.begin_drawing(&thread);

        d.clear_background(Color::BLACK);
        d.draw_text("Khanqah Rush", 12, 12, 20, Color::RAYWHITE);
    }
}
