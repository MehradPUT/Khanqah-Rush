// Builds the Raylib + Rust game frontend into public/game/ for serving.
// Tolerant by design (same policy as build-wasm.mjs): without the
// Emscripten toolchain it warns and skips so contributors without it can
// still work — the legacy PIXI frontend remains the default entry.
//
// Windows notes (empirically derived, emsdk 6.x + raylib-sys 6.0):
// - EMCC_CFLAGS is mandatory (raylib-sys build script demands it).
// - CC/CXX must point at emcc.exe/em++.exe: otherwise the cc crate
//   wraps the compiler as `cmd /c emcc.bat` and cmake chokes on the
//   leaked `/c emcc.bat` flags.
// - AR must point at emar.exe (cc guesses `emar.bat`, which no longer
//   ships with emsdk).
// - BINDGEN_EXTRA_CLANG_ARGS needs the emscripten sysroot with FORWARD
//   slashes (backslashes die in shlex unescaping) so bindgen finds
//   system headers like math.h.
// - RUSTFLAGS linker must be emcc.exe: rustc invokes `emcc.bat`,
//   which no longer ships with emsdk.
// - Let emcmake default to MinGW Makefiles (Ninja is rejected by the
//   emscripten toolchain file on Windows).
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

const TARGET = "wasm32-unknown-emscripten";
const release = process.argv.includes("--release");
const profile = release ? "release" : "debug";

// The emsdk location is NEVER hardcoded: it comes from the EMSDK
// environment variable or from wherever `emcc` resolves on PATH.
function emsdkBin(name) {
	if (process.env.EMSDK) {
		const direct = join(process.env.EMSDK, "upstream/emscripten", name);
		if (existsSync(direct)) {
			return direct;
		}
	}
	try {
		const found = execFileSync(
			process.platform === "win32" ? "where" : "which",
			["emcc"],
			{ encoding: "utf8" },
		)
			.split(/\r?\n/)
			.map((line) => line.trim())
			.filter(Boolean);
		for (const candidate of found) {
			const sibling = join(dirname(candidate), name);
			if (existsSync(sibling)) {
				return sibling;
			}
		}
	} catch {
		// Fall through to the skip message below.
	}
	return null;
}

function haveToolchain() {
	try {
		execFileSync("cargo", ["--version"], { stdio: "ignore" });
		const targets = execFileSync("rustup", ["target", "list", "--installed"], {
			encoding: "utf8",
		});
		if (!targets.split(/\r?\n/).includes(TARGET)) {
			return false;
		}
		return ["emcc.exe", "em++.exe", "emar.exe"].every(
			(tool) => emsdkBin(tool) !== null,
		);
	} catch {
		return false;
	}
}

if (!haveToolchain()) {
	console.warn(
		"[frontend] emscripten toolchain or the wasm32-unknown-emscripten " +
			"target is missing, skipping the Raylib frontend build. Set the " +
			"EMSDK environment variable (or put emcc on PATH) to enable it. " +
			"The legacy frontend stays the default entry.",
	);
	process.exit(0);
}

const emccExe = emsdkBin(process.platform === "win32" ? "emcc.exe" : "emcc");
const emDir = dirname(emccExe);
const toPosix = (p) => p.replaceAll("\\", "/");
const env = {
	...process.env,
	EMCC_CFLAGS:
		"-O3 -sUSE_GLFW=3 -sASSERTIONS=1 -sWASM=1 -sASYNCIFY -sGL_ENABLE_GET_PROC_ADDRESS=1",
	CC_wasm32_unknown_emscripten: emccExe,
	CXX_wasm32_unknown_emscripten: join(
		emDir,
		process.platform === "win32" ? "em++.exe" : "em++",
	),
	AR_wasm32_unknown_emscripten: join(
		emDir,
		process.platform === "win32" ? "emar.exe" : "emar",
	),
	BINDGEN_EXTRA_CLANG_ARGS: `--sysroot=${toPosix(join(emDir, "cache/sysroot"))}`,
	RUSTFLAGS: `${process.env.RUSTFLAGS ?? ""} -C linker=${emccExe}`.trim(),
};

execFileSync(
	"cargo",
	["build", ...(release ? ["--release"] : []), "--target", TARGET],
	{ stdio: "inherit", cwd: "frontend", env },
);

const outDir = `frontend/target/${TARGET}/${profile}`;
for (const file of ["khanqah-frontend.js", "khanqah_frontend.wasm"]) {
	const artifact = join(outDir, file);
	if (!existsSync(artifact)) {
		console.error(`[frontend] expected artifact missing: ${artifact}`);
		process.exit(1);
	}
}
mkdirSync("public/game", { recursive: true });
copyFileSync(join(outDir, "khanqah-frontend.js"), "public/game/khanqah-frontend.js");
copyFileSync(join(outDir, "khanqah_frontend.wasm"), "public/game/khanqah_frontend.wasm");
console.log("[frontend] wrote public/game/khanqah-frontend.js + .wasm");
