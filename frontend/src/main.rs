//! Khanqah Rush frontend: Raylib + Rust, compiled to WASM.
//!
//! Phase 3 plays one endless Nima run per page load: arrows/AD/HL or
//! half-screen taps chop, death shows the died sprite, any input starts
//! a fresh round. Carousel, HUD chrome, audio, and score reporting land
//! in later phases (see docs/frontend-raylib.md).

mod assets;
mod game;
mod layout;
mod scene;

use game::Game;
use layout::Layout;
use raylib::prelude::*;

/// Browser resize hook for the shell page (`khanqah_fitCanvas`).
/// Exported but optional: the shell guards its presence.
#[no_mangle]
pub extern "C" fn khanqah_resize(w: i32, h: i32) {
    unsafe {
        raylib::ffi::SetWindowSize(w, h);
    }
}

fn chop_side(rl: &RaylibHandle) -> Option<bool> {
    use KeyboardKey::*;
    if rl.is_key_pressed(KEY_LEFT)
        || rl.is_key_pressed(KEY_A)
        || rl.is_key_pressed(KEY_H)
    {
        return Some(true);
    }
    if rl.is_key_pressed(KEY_RIGHT)
        || rl.is_key_pressed(KEY_D)
        || rl.is_key_pressed(KEY_L)
    {
        return Some(false);
    }
    if rl.is_mouse_button_pressed(MouseButton::MOUSE_BUTTON_LEFT) {
        let x = rl.get_mouse_position().x;
        return Some(x < rl.get_screen_width() as f32 / 2.0);
    }
    None
}

fn main() {
    let (mut rl, thread) = raylib::init()
        .size(800, 600)
        .title("Khanqah Rush")
        .build();
    rl.set_target_fps(60);

    let tex = scene::Textures::load(&mut rl, &thread);
    let mut game = Game::new_round();

    while !rl.window_should_close() {
        // Input: chop, or restart after death.
        if let Some(left) = chop_side(&rl) {
            if game.alive() {
                let t_ms = (rl.get_time() * 1000.0) as u32;
                game.chop(left, t_ms);
            } else {
                game = Game::new_round();
            }
        }
        // Idle clock so exhaustion can end the round.
        if game.alive() {
            let t_ms = (rl.get_time() * 1000.0) as u32;
            game.sim.advance_idle(t_ms);
        }

        let layout = Layout::compute(
            rl.get_screen_width(),
            rl.get_screen_height(),
            game.sim.shifts,
        );
        let mut d = rl.begin_drawing(&thread);
        scene::draw_scene(&mut d, &tex, &game, &layout);
    }
}



// touch
