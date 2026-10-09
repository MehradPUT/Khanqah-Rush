//! Asset paths + loading.
//!
//! Emscripten build preloads `public/images|sounds|fonts` at the virtual
//! roots `/images` etc. plus rasterized bundle SVGs at `/art` (see
//! scripts/build-frontend.mjs). Native dev runs resolve the same files
//! from the repo tree (run cargo from `frontend/`).

/// Resolve a game asset path for this target.
pub fn path(dir: &str, file: &str) -> String {
    #[cfg(target_os = "emscripten")]
    return format!("/{dir}/{file}");
    #[cfg(not(target_os = "emscripten"))]
    return format!("../public/{dir}/{file}");
}

/// Rasterized bundle SVG art (`tmp/frontend-art` natively).
pub fn art(file: &str) -> String {
    #[cfg(target_os = "emscripten")]
    return format!("/art/{file}");
    #[cfg(not(target_os = "emscripten"))]
    return format!("../tmp/frontend-art/{file}");
}
