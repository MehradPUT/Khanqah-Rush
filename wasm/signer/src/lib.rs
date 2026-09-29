//! Khanqah Rush score-signer stub, compiled to WASM.
//!
//! The real HMAC-SHA256 signing lands with the signed-score task. This stub
//! only proves the toolchain (cargo → wasm32-unknown-unknown) and the
//! TypeScript loader wiring. It is loaded with plain `WebAssembly` —
//! no wasm-bindgen / wasm-pack glue.

/// Wire-format version. The TS loader refuses anything else.
#[no_mangle]
pub extern "C" fn signer_version() -> u32 {
    1
}

/// Placeholder transform. The real `sign(score, nonce, timestamp) -> mac`
/// replaces this once the secret-injection design is implemented.
#[no_mangle]
pub extern "C" fn sign_score_stub(score: u32) -> u32 {
    score ^ 0x5A5A5A5A
}
