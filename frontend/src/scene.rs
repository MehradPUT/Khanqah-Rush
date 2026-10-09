//! Canvas scene: background, tree, lumberjack, score, stamina.
//!
//! Layout ports the legacy bundle's `Pa()` numbers 1:1 (see
//! docs/bundle-map.md + layout.rs). Deliberate simplifications for
//! Phase 3, all marked: tiling replaced by stretch for gradient art,
//! branch spacing uniform (no sprite bookkeeping — that bookkeeping
//! IS the invisible-branches bug), no tweens (end-states only),
//! single ground strip instead of the conditional second canvas.

use crate::{assets, game::Game, layout::Layout};
use khanqah_sim::SIDE_NONE;
use raylib::prelude::*;

const BG: Color = Color::new(0x0e, 0x12, 0x20, 255);
const WHITE: Color = Color::new(255, 255, 255, 255);
const BLACK: Color = Color::new(0, 0, 0, 255);

pub struct Textures {
    pub trunk: Texture2D,
    pub branch: Texture2D,
    pub bg_bottom: Texture2D,
    pub bg_clouds: Texture2D,
    pub bg_trees: Texture2D,
    pub ground_bg: Texture2D,
    pub ground_left: Texture2D,
    pub ground_right: Texture2D,
    pub stumb: Texture2D,
    pub stones: Texture2D,
    pub nima_body: Texture2D,
    pub nima_died: Texture2D,
    pub timeline: Texture2D,
    pub timeline_bar: Texture2D,
    pub timeline_warn: Texture2D,
    pub font: Font,
}

impl Textures {
    pub fn load(rl: &mut RaylibHandle, thread: &RaylibThread) -> Self {
        fn tex(rl: &mut RaylibHandle, thread: &RaylibThread, path: String) -> Texture2D {
            rl.load_texture(thread, &path).expect("scene texture")
        }
        let font = rl
            .load_font_ex(
                thread,
                &assets::path("fonts", "CharterBT-Bold.ttf"),
                20,
                None,
            )
            .expect("score font");
        Self {
            trunk: tex(rl, thread, assets::art("trunk.png")),
            branch: tex(rl, thread, assets::art("branch.png")),
            bg_bottom: tex(rl, thread, assets::art("bg_bottom.png")),
            bg_clouds: tex(rl, thread, assets::art("bg_clouds.png")),
            bg_trees: tex(rl, thread, assets::art("bg_trees.png")),
            ground_bg: tex(rl, thread, assets::art("ground_bg.png")),
            ground_left: tex(rl, thread, assets::art("ground_left.png")),
            ground_right: tex(rl, thread, assets::art("ground_right.png")),
            stumb: tex(rl, thread, assets::art("stumb.png")),
            stones: tex(rl, thread, assets::art("stones.png")),
            nima_body: tex(rl, thread, assets::path("images", "nima_body_old.png")),
            nima_died: tex(rl, thread, assets::path("images", "nima_died_old.png")),
            timeline: tex(rl, thread, assets::art("timeline.png")),
            timeline_bar: tex(rl, thread, assets::art("timeline_bar.png")),
            timeline_warn: tex(rl, thread, assets::art("timeline_warn.png")),
            font,
        }
    }
}

/// Stretched blit of a full texture into a dest rect.
fn blit(d: &mut impl RaylibDraw, tex: &Texture2D, x: f32, y: f32, w: f32, h: f32) {
    d.draw_texture_pro(
        tex,
        Rectangle::new(0.0, 0.0, tex.width as f32, tex.height as f32),
        Rectangle::new(x, y, w, h),
        Vector2::new(0.0, 0.0),
        0.0,
        WHITE,
    );
}

pub fn draw_scene(d: &mut impl RaylibDraw, tex: &Textures, game: &Game, l: &Layout) {
    d.clear_background(BG);
    let cx = l.cx();
    let h = l.h as f32;

    // Background layers (bundle O/P/E regions, stretched).
    blit(d, &tex.bg_bottom, l.ox as f32, 0.0, l.d as f32, h);
    blit(d, &tex.bg_clouds, l.ox as f32, h - 130.0, l.d as f32, 90.0);
    blit(d, &tex.bg_trees, l.ox as f32, h - 128.0, l.d as f32, 128.0);

    // Trunk column (100 wide), tiled from the top down to the base.
    let trunk_w = 100.0;
    let trunk_h = 750.0;
    let mut y = l.base_y;
    while y > 0.0 {
        y -= trunk_h;
        blit(d, &tex.trunk, cx - trunk_w / 2.0, y.max(0.0), trunk_w, (l.base_y - y).min(trunk_h));
    }

    // Branches, one sprite per nonzero pair, bottom-up every 80 px.
    let segs = game.sim.segments();
    let pairs = segs.len() / 2;
    for k in 0..pairs {
        let a = segs[2 * k];
        let b = segs[2 * k + 1];
        let side = if a != SIDE_NONE {
            a
        } else if b != SIDE_NONE {
            b
        } else {
            continue;
        };
        let by = l.base_y - 40.0 - k as f32 * 80.0;
        if by < -100.0 {
            break;
        }
        // 125x80 sprite; LEFT extends left, RIGHT extends right.
        let (dx, flip) = if side < 0 {
            (cx - 135.0, true)
        } else {
            (cx + 10.0, false)
        };
        let sw = if flip { -125.0 } else { 125.0 };
        d.draw_texture_pro(
            &tex.branch,
            Rectangle::new(0.0, 0.0, tex.branch.width as f32, tex.branch.height as f32),
            Rectangle::new(if flip { dx + 125.0 } else { dx }, by - 80.0, sw, 80.0),
            Vector2::new(0.0, 0.0),
            0.0,
            WHITE,
        );
    }

    // Lumberjack (static side; Nima only in Phase 3).
    let body = if game.alive() {
        &tex.nima_body
    } else {
        &tex.nima_died
    };
    let (bw, bh) = (68.0, 140.0);
    blit(d, body, cx + 35.0 - bw / 2.0, l.base_y - bh, bw, bh);

    // Score + stamina HUD (bundle Q/n/A geometry).
    let score = game.score().to_string();
    let tw = tex.font.measure_text(&score, 20.0, 0.0).x;
    d.draw_text_ex(&tex.font, &score, Vector2::new(cx - tw / 2.0, 30.0), 20.0, 0.0, WHITE);

    let stamina = (game.sim.stamina_left_ms() as f64 / game.sim.qa_ms).clamp(0.0, 1.0) as f32;
    let ax = cx - 44.0;
    let ay = 15.0;
    d.draw_rectangle(ax as i32 - 3, ay as i32 - 3, 94, 15, BLACK);
    blit(d, &tex.timeline_bar, ax, ay + 3.0, 88.0 * stamina, 9.0);
    if stamina < 0.25 {
        blit(d, &tex.timeline_warn, ax, ay + 3.0, 88.0 * stamina, 9.0);
    }
    blit(d, &tex.timeline, ax - 6.0, ay - 6.0, 100.0, 21.0);

    // Ground strip (bundle 170px ground canvas, always drawn).
    let gy = h - 95.0;
    blit(d, &tex.ground_bg, 0.0, gy, l.w as f32, 95.0);
    blit(d, &tex.ground_left, 0.0, gy, 140.0, 95.0);
    blit(d, &tex.ground_right, l.w as f32 - 195.0, gy, 195.0, 95.0);
    blit(d, &tex.stumb, cx - 120.0, h - 60.0, 50.0, 60.0);
    blit(d, &tex.stones, cx + 60.0, h - 36.0, 75.0, 36.0);
}
