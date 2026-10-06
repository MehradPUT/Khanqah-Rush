//! Khanqah Rush score signer (WASM, no-bindgen).
//!
//! Holds a per-session HMAC-SHA256 key in linear memory and tags canonical
//! score envelopes. The key is issued by the server at launch and lives only
//! for the session — the binary carries no long-term secret. Loaded over
//! plain `WebAssembly`, no wasm-bindgen / wasm-pack glue.

use hmac::{Hmac, KeyInit, Mac};
use sha2::Sha256;

type HmacSha256 = Hmac<Sha256>;

pub const WIRE_VERSION: u32 = 2;
pub const KEY_LEN: usize = 32;
pub const MAX_MSG_LEN: usize = 512;
pub const TAG_LEN: usize = 32;

static mut SESSION_KEY: [u8; KEY_LEN] = [0; KEY_LEN];
static mut SESSION_SET: bool = false;
static mut MSG_BUF: [u8; MAX_MSG_LEN] = [0; MAX_MSG_LEN];
static mut TAG_BUF: [u8; TAG_LEN] = [0; TAG_LEN];

/// Wire-format version. The TS loader refuses anything else.
#[no_mangle]
pub extern "C" fn signer_version() -> u32 {
    WIRE_VERSION
}

/// Byte capacity of the message scratch buffer.
#[no_mangle]
pub extern "C" fn max_msg_len() -> usize {
    MAX_MSG_LEN
}

/// Copies a 32-byte session key into memory. Returns 0 on success,
/// 1 on null pointer or wrong length.
#[no_mangle]
pub unsafe extern "C" fn init_session(key_ptr: *const u8, key_len: usize) -> u32 {
    if key_ptr.is_null() || key_len != KEY_LEN {
        return 1;
    }
    let src = core::slice::from_raw_parts(key_ptr, key_len);
    let dst = &mut *core::ptr::addr_of_mut!(SESSION_KEY);
    dst.copy_from_slice(src);
    *core::ptr::addr_of_mut!(SESSION_SET) = true;
    0
}

/// Pointer to the message scratch buffer (write canonical bytes here).
#[no_mangle]
pub extern "C" fn msg_buffer_ptr() -> *mut u8 {
    core::ptr::addr_of_mut!(MSG_BUF).cast()
}

/// Pointer to the 32-byte tag buffer (valid after a successful sign_tag).
#[no_mangle]
pub extern "C" fn tag_buffer_ptr() -> *const u8 {
    core::ptr::addr_of!(TAG_BUF).cast()
}

/// Tags `MSG_BUF[..msg_len]` with the session key into `TAG_BUF`.
/// Returns 0 on success, 1 with no session, 2 when the message is too long.
#[no_mangle]
pub extern "C" fn sign_tag(msg_len: usize) -> u32 {
    if msg_len > MAX_MSG_LEN {
        return 2;
    }
    let has_session = unsafe { *core::ptr::addr_of!(SESSION_SET) };
    if !has_session {
        return 1;
    }
    let mut mac = unsafe {
        let key = &*core::ptr::addr_of!(SESSION_KEY);
        HmacSha256::new_from_slice(key).expect("session key is 32 bytes")
    };
    let msg = unsafe { &*core::ptr::addr_of!(MSG_BUF) };
    mac.update(&msg[..msg_len]);
    let tag = mac.finalize().into_bytes();
    unsafe {
        let out = &mut *core::ptr::addr_of_mut!(TAG_BUF);
        out.copy_from_slice(&tag);
    }
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rfc4231_hmac_sha256_case1() {
        // Key = 20 x 0x0b, data = "Hi There".
        let mut mac = HmacSha256::new_from_slice(&[0x0bu8; 20]).unwrap();
        mac.update(b"Hi There");
        let expected: [u8; 32] = [
            0xb0, 0x34, 0x4c, 0x61, 0xd8, 0xdb, 0x38, 0x53, 0x5c, 0xa8, 0xaf, 0xce, 0xaf, 0x0b,
            0xf1, 0x2b, 0x88, 0x1d, 0xc2, 0x00, 0xc9, 0x83, 0x3d, 0xa7, 0x26, 0xe9, 0x37, 0x6c,
            0x2e, 0x32, 0xcf, 0xf7,
        ];
        assert_eq!(mac.finalize().into_bytes().as_slice(), &expected);
    }

    #[test]
    fn session_flow_matches_direct_hmac() {
        // Error paths first (no session yet at this point only if this is
        // the first session test to run — keep all stateful steps here).
        assert_eq!(unsafe { sign_tag(1) }, 1);
        assert_eq!(unsafe { init_session(core::ptr::null(), 32) }, 1);
        assert_eq!(unsafe { init_session([0u8; 32].as_ptr(), 31) }, 1);

        let key = [0x42u8; KEY_LEN];
        assert_eq!(unsafe { init_session(key.as_ptr(), key.len()) }, 0);

        let msg = b"khanqah-v1\nsid\n250\n12\nnonce\n1700000000";
        assert!(msg.len() <= unsafe { max_msg_len() });
        unsafe {
            let dst = &mut *core::ptr::addr_of_mut!(MSG_BUF);
            dst[..msg.len()].copy_from_slice(msg);
        }
        assert_eq!(unsafe { sign_tag(msg.len()) }, 0);
        assert_eq!(unsafe { sign_tag(MAX_MSG_LEN + 1) }, 2);

        let got = unsafe { &*core::ptr::addr_of!(TAG_BUF) };
        let mut mac = HmacSha256::new_from_slice(&key).unwrap();
        mac.update(msg);
        assert_eq!(got.as_slice(), mac.finalize().into_bytes().as_slice());
        assert_eq!(unsafe { signer_version() }, WIRE_VERSION);
    }
}
