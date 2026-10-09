//! Khanqah Rush frontend: Raylib + Rust, compiled to WASM.
//!
//! Phase 3 plays endless Nima rounds: Space/tap starts (the game never
//! starts itself), arrows/AD/HL or half-screen taps chop, death shows
//! the died sprite, any input starts a fresh round. Carousel, HUD
//! chrome, audio, and score reporting land in later phases (see
//! docs/frontend-raylib.md).

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

fn start_pressed(rl: &RaylibHandle) -> bool {
    use KeyboardKey::*;
    rl.is_key_pressed(KEY_SPACE) || rl.is_mouse_button_pressed(MouseButton::MOUSE_BUTTON_LEFT)
}

fn main() {
    let (mut rl, thread) = raylib::init()
        .size(800, 600)
        .title("Khanqah Rush")
        .build();
    rl.set_target_fps(60);

    let tex = scene::Textures::load(&mut rl, &thread);
    // Cold boot shows one fixed idle scene (stable seed, no flicker);
    // the first Space/tap starts live play.
    let idle = Game::new_round();
    let mut game: Option<Game> = None;

    while !rl.window_should_close() {
        // Input: chop, restart after death, or start from boot.
        let mut restart = false;
        if let Some(game) = game.as_mut() {
            if game.alive() {
                if let Some(left) = chop_side(&rl) {
                    let t_ms = (rl.get_time() * 1000.0) as u32;
                    game.chop(left, t_ms);
                }
                // Idle clock so exhaustion can end the round.
                let t_ms = (rl.get_time() * 1000.0) as u32;
                game.sim.advance_idle(t_ms);
            } else if start_pressed(&rl) || chop_side(&rl).is_some() {
                restart = true;
            }
        } else if start_pressed(&rl) {
            restart = true;
        }
        if restart {
            game = Some(Game::new_round());
        }

        let sim = game.as_ref().map(|g| &g.sim);
        let shifts = sim.map(|s| s.shifts).unwrap_or(0);
        let layout = Layout::compute(
            rl.get_screen_width(),
            rl.get_screen_height(),
            shifts,
        );
        let mut d = rl.begin_drawing(&thread);
        let g = game.as_ref().unwrap_or(&idle);
        scene::draw_scene(&mut d, &tex, g, &layout, game.is_none());
    }
}
