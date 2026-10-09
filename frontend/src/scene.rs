//! Canvas scene: background, tree, lumberjack, score, stamina.
//!
//! Layout ports the legacy bundle's `Pa()` numbers (see docs/bundle-map.md
//! and layout.rs). Composition rules learned from screenshots:
//! - light-blue sky base; cloud/tree bands tiled, never stretched;
//! - the tree container descends with chops (W) while the mound, the
//!   lumberjack, and the HUD stay fixed; branches vanish behind the
//!   mound, which is drawn after the tree;
//! - one canopy chunk per nonzero pair at the trunk edge, mirrored;
//! - lumberjack bottom-left anchored, facing outward.
//! Still simplified: no tweens (end-states), no particles, Nima only.

use crate::{assets, game::Game, layout::Layout};
use khanqah_sim::SIDE_NONE;
use raylib::prelude::*;

const SKY: Color = Color::new(0xc7, 0xf0, 0xf9, 255);
const INK: Color = Color::new(0x37, 0x47, 0x4f, 255);
const PILL: Color = Color::new(0x1e, 0x2a, 0x38, 255);
const SUN: Color = Color::new(0xff, 0xd7, 0x6a, 255);
const LEAF: Color = Color::new(0x4c, 0xaf, 0x50, 255);
const WHITE: Color = Color::new(255, 255, 255, 255);

pub struct Textures {
    pub trunk: Texture2D,
    pub branch_left: Texture2D,
    pub branch_right: Texture2D,
    pub bg_bottom: Texture2D,
    pub bg_clouds: Texture2D,
    pub bg_trees: Texture2D,
    pub ground_bg: Texture2D,
    pub ground_left: Texture2D,
    pub ground_right: Texture2D,
    pub stumb: Texture2D,
    pub stones: Texture2D,
    pub nima_body: Texture2D,
    pub nima_body_flip: Texture2D,
    pub nima_died: Texture2D,
    pub nima_died_flip: Texture2D,
    pub font: Font,
}

impl Textures {
    pub fn load(rl: &mut RaylibHandle, thread: &RaylibThread) -> Self {
        fn tex(rl: &mut RaylibHandle, thread: &RaylibThread, path: String) -> Texture2D {
            rl.load_texture(thread, &path).expect("scene texture")
        }
        /// Load twice: native and horizontally mirrored (raylib has no
        /// reliable runtime mirror for our targets; see flip attempts).
        fn tex_pair(
            rl: &mut RaylibHandle,
            thread: &RaylibThread,
            path: String,
        ) -> (Texture2D, Texture2D) {
            let mut img = Image::load_image(&path).expect("scene image");
            let normal = rl
                .load_texture_from_image(thread, &img)
                .expect("scene texture");
            img.flip_horizontal();
            let mirrored = rl
                .load_texture_from_image(thread, &img)
                .expect("scene texture");
            (normal, mirrored)
        }
        let font = rl
            .load_font_ex(
                thread,
                &assets::path("fonts", "CharterBT-Bold.ttf"),
                20,
                None,
            )
            .expect("score font");
        let (branch_right, branch_left) =
            tex_pair(rl, thread, assets::art("branch.png"));
        let (nima_body, nima_body_flip) = tex_pair(
            rl,
            thread,
            assets::path("images", "nima_body_old.png"),
        );
        let (nima_died, nima_died_flip) = tex_pair(
            rl,
            thread,
            assets::path("images", "nima_died_old.png"),
        );
        Self {
            trunk: tex(rl, thread, assets::art("trunk.png")),
            branch_left,
            branch_right,
            bg_bottom: tex(rl, thread, assets::art("bg_bottom.png")),
            bg_clouds: tex(rl, thread, assets::art("bg_clouds.png")),
            bg_trees: tex(rl, thread, assets::art("bg_trees.png")),
            ground_bg: tex(rl, thread, assets::art("ground_bg.png")),
            ground_left: tex(rl, thread, assets::art("ground_left.png")),
            ground_right: tex(rl, thread, assets::art("ground_right.png")),
            stumb: tex(rl, thread, assets::art("stumb.png")),
            stones: tex(rl, thread, assets::art("stones.png")),
            nima_body,
            nima_body_flip,
            nima_died,
            nima_died_flip,
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

pub fn draw_scene(
    d: &mut impl RaylibDraw,
    tex: &Textures,
    game: &Game,
    l: &Layout,
    waiting: bool,
) {
    d.clear_background(SKY);
    let cx = l.cx();
    let h = l.h as f32;
    let ox = l.ox as f32;
    let dw = l.d as f32;

    // Sky + bands, tiled.
    tile_region(d, &tex.bg_bottom, ox, 0.0, dw, h, 420.0, 180.0);
    tile_region(d, &tex.bg_clouds, ox, h - 260.0, dw, 130.0, 950.0, 256.0);
    tile_region(d, &tex.bg_trees, ox, h - 256.0, dw, 128.0, 840.0, 280.0);

    // Trunk column (100 wide), tiled down past the mound line.
    tile_region(d, &tex.trunk, cx - 50.0, 0.0, 100.0, l.base_y, 100.0, 750.0);

    // Branches: one canopy chunk per nonzero pair, bottom-up every
    // 80 px, bottom-left anchored at the trunk edge, stub inward.
    // Pairs at/below the mound top stay hidden behind it.
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
        if by < -100.0 || by > l.mound_top {
            continue;
        }
        let chunk = if side < 0 {
            &tex.branch_left
        } else {
            &tex.branch_right
        };
        let dx = if side < 0 { cx - 135.0 } else { cx + 10.0 };
        blit(d, chunk, dx, by - 80.0, 125.0, 80.0);
    }

    // Ground mound (drawn after the tree so the base sinks behind it).
    let mound_h = 110.0;
    blit(d, &tex.ground_bg, ox, l.mound_top, dw, mound_h);
    blit(d, &tex.ground_left, ox, l.mound_top, 140.0, 95.0);
    blit(
        d,
        &tex.ground_right,
        ox + dw - 195.0,
        l.mound_top,
        195.0,
        95.0,
    );
    blit(d, &tex.stumb, cx - 110.0, l.mound_top - 60.0, 50.0, 60.0);
    blit(d, &tex.stones, cx - 40.0, l.mound_top - 36.0, 75.0, 36.0);

    // Lumberjack, bottom-left anchored on the mound, facing outward.
    // The side follows every processed chop (bundle tail wa()).
    let left = game.sim.player_left;
    let body = if game.alive() {
        if left {
            &tex.nima_body
        } else {
            &tex.nima_body_flip
        }
    } else if left {
        &tex.nima_died
    } else {
        &tex.nima_died_flip
    };
    let bx = if left { cx - 35.0 - 68.0 } else { cx + 35.0 };
    blit(d, body, bx, l.mound_top - 140.0, 68.0, 140.0);

    // Score, dark like the legacy HUD, centered below the pill.
    let score = game.score().to_string();
    let tw = tex.font.measure_text(&score, 20.0, 0.0).x;
    d.draw_text_ex(
        &tex.font,
        &score,
        Vector2::new(cx - tw / 2.0, 42.0),
        20.0,
        0.0,
        INK,
    );

    // Stamina pill, centered: dark chip, yellow seconds, green bar.
    let stamina =
        (game.sim.stamina_left_ms() as f64 / game.sim.qa_ms).clamp(0.0, 1.0) as f32;
    let px = cx - 60.0;
    let py = 8.0;
    d.draw_rectangle_rounded(Rectangle::new(px, py, 120.0, 26.0), 0.45, 8, PILL);
    let secs = (game.sim.stamina_left_ms() / 1000).to_string() + "s";
    d.draw_text_ex(&tex.font, &secs, Vector2::new(px + 8.0, py + 4.0), 18.0, 0.0, SUN);
    d.draw_rectangle(
        px as i32 + 8,
        py as i32 + 30,
        (104.0 * stamina) as i32,
        6,
        LEAF,
    );

    if waiting {
        let prompt = "tap or press space";
        let pw = tex.font.measure_text(prompt, 20.0, 0.0).x;
        d.draw_text_ex(
            &tex.font,
            prompt,
            Vector2::new(cx - pw / 2.0, h / 2.0),
            20.0,
            0.0,
            INK,
        );
    }

    // TEMP-DEBUG (Phase 3): backing-store dimensions on canvas so one
    // screenshot settles every sizing question. Remove after parity.
    let dims = format!("{}x{} d{} ox{}", l.w, l.h, l.d, l.ox);
    d.draw_text_ex(
        &tex.font,
        &dims,
        Vector2::new(6.0, h - 20.0),
        10.0,
        0.0,
        INK,
    );
}
