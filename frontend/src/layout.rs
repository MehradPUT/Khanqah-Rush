//! Scene layout, ported from the legacy bundle's `Pa()` sizing.
//!
//! Units are bundle pixels. The scene column `d` is centered in the
//! viewport (`ox`); heights use the full viewport. Deviations from the
//! legacy dual-canvas page are noted inline; screenshots judge parity.

/// Computed layout for one frame.
pub struct Layout {
    /// Viewport size.
    pub w: i32,
    pub h: i32,
    /// Scene column width (bundle caps at 800) and its x offset.
    pub d: i32,
    pub ox: i32,
    /// Tree container base y (bundle `u.y = f-55+W`, W from shifts).
    pub base_y: f32,
}

impl Layout {
    pub fn compute(w: i32, h: i32, shifts: u64) -> Self {
        let d = w.min(800);
        let ox = (w - d) / 2;
        Self {
            w,
            h,
            d,
            ox,
            base_y: h as f32 - 55.0 + shifts as f32 * 50.0,
        }
    }

    /// Scene-column center x in viewport pixels.
    pub fn cx(&self) -> f32 {
        self.ox as f32 + self.d as f32 / 2.0
    }
}
