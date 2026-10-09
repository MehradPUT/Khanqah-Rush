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

/// Tiled blit clipped to a region (bundle TilingSprite equivalent).
/// Tile art is rasterized at 2x, so `tw`/`th` are bundle units.
fn tile_region(
    d: &mut impl RaylibDraw,
    tex: &Texture2D,
    rx: f32,
    ry: f32,
    rw: f32,
    rh: f32,
    tw: f32,
    th: f32,
) {
    if rw <= 0.0 || rh <= 0.0 {
        return;
    }
    let sx = tex.width as f32 / tw;
    let sy = tex.height as f32 / th;
    let mut y = ry;
    while y < ry + rh {
        let mut x = rx;
        while x < rx + rw {
            let w = (rx + rw - x).min(tw);
            let h = (ry + rh - y).min(th);
            d.draw_texture_pro(
                tex,
                Rectangle::new((x - rx) * sx, (y - ry) * sy, w * sx, h * sy),
                Rectangle::new(x, y, w, h),
                Vector2::new(0.0, 0.0),
                0.0,
                WHITE,
            );
            x += tw;
        }
        y += th;
    }
}

pub fn draw_scene(d: &mut impl RaylibDraw, tex: &Textures, game: &Game, l: &Layout) {
    d.clear_background(BG);
    let cx = l.cx();
    let h = l.h as f32;
    let ox = l.ox as f32;
    let dw = l.d as f32;

    // Background layers, tiled like the bundle (never stretched —
    // stretching the cloud motif is what produced the blobs).
    tile_region(d, &tex.bg_bottom, ox, 0.0, dw, h, 420.0, 180.0);
    tile_region(d, &tex.bg_clouds, ox, h - 130.0, dw, 90.0, 950.0, 256.0);
    tile_region(d, &tex.bg_trees, ox, h - 128.0, dw, 128.0, 840.0, 280.0);

    // Trunk column (100 wide), tiled down to the base.
    tile_region(d, &tex.trunk, cx - 50.0, 0.0, 100.0, l.base_y, 100.0, 750.0);

    // Branches: one canopy chunk per nonzero pair, bottom-up every
    // 80 px, anchored bottom-left at the trunk edge and mirrored by
    // side (stub faces the trunk). Source-flip: the canonical
    // raylib mirror, unlike negative dest widths.
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
        let tw = tex.branch.width as f32;
        let th = tex.branch.height as f32;
        if side < 0 {
            // LEFT chunk: bottom-left corner at trunk edge, mirrored.
            d.draw_texture_pro(
                &tex.branch,
                Rectangle::new(tw, 0.0, -tw, th),
                Rectangle::new(cx - 135.0, by - 80.0, 125.0, 80.0),
                Vector2::new(0.0, 0.0),
                0.0,
                WHITE,
            );
        } else {
            d.draw_texture_pro(
                &tex.branch,
                Rectangle::new(0.0, 0.0, tw, th),
                Rectangle::new(cx + 10.0, by - 80.0, 125.0, 80.0),
                Vector2::new(0.0, 0.0),
                0.0,
                WHITE,
            );
        }
    }

    // Lumberjack, bottom-left anchored (bundle `sa` anchor): right of
    // the trunk on the initial side, mirrored to face outward.
    let body = if game.alive() {
        &tex.nima_body
    } else {
        &tex.nima_died
    };
    let bw = body.width as f32;
    let bh = body.height as f32;
    d.draw_texture_pro(
        body,
        Rectangle::new(bw, 0.0, -bw, bh),
        Rectangle::new(cx + 35.0, l.base_y - 140.0, 68.0, 140.0),
        Vector2::new(0.0, 0.0),
        0.0,
        WHITE,
    );

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
