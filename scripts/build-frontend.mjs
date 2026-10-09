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
import {
	copyFileSync,
	existsSync,
	mkdirSync,
	readFileSync,
	readdirSync,
	statSync,
	unlinkSync,
	writeFileSync,
} from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

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
// Absolute repo root (this script lives in <root>/scripts/).
const rootDir = join(dirname(fileURLToPath(import.meta.url)), "..");

// SVG art (extracted from the legacy bundle) rasterized at 2x, then
// preloaded with the rest of public/ into the emscripten virtual FS.
function rasterizeArt() {
	try {
		execFileSync("rsvg-convert", ["--version"], { stdio: "ignore" });
	} catch {
		console.warn(
			"[frontend] rsvg-convert missing, skipping the Raylib frontend " +
				"build (SVG art cannot rasterize).",
		);
		process.exit(0);
	}
	const srcDir = join(rootDir, "frontend/assets");
	const outDir = join(rootDir, "tmp/frontend-art");
	mkdirSync(outDir, { recursive: true });
	for (const file of readdirSync(srcDir).filter((f) => f.endsWith(".svg"))) {
		const svg = readFileSync(join(srcDir, file), "utf8").slice(0, 2000);
		const dims =
			svg.match(/width="([\d.]+)(?:px)?"\s+height="([\d.]+)/) ||
			svg.match(/viewBox="[\d.\s-]+ ([\d.]+) ([\d.]+)"/);
		if (!dims) {
			console.error(`[frontend] no size in ${file}`);
			process.exit(1);
		}
		const out = join(outDir, file.replace(/\.svg$/, ".png"));
		execFileSync("rsvg-convert", [
			"-w",
			String(Math.round(Number(dims[1]) * 2)),
			"-h",
			String(Math.round(Number(dims[2]) * 2)),
			"-o",
			out,
			join(srcDir, file),
		]);
	}
	return outDir;
}
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
	RUSTFLAGS:
		`${process.env.RUSTFLAGS ?? ""} -C linker=${emccExe}`.trim(),
};

// Preloaded virtual FS: bundle-relative art dirs plus rasterized SVGs.
// The game reads these through the asset() helper (see frontend/).
const artDir = rasterizeArt();
const preloads = [
	[join(rootDir, "public/images"), "/images"],
	[join(rootDir, "public/sounds"), "/sounds"],
	[join(rootDir, "public/fonts"), "/fonts"],
	[artDir, "/art"],
];
for (const [src, dst] of preloads) {
	env.RUSTFLAGS += ` -C link-args=--preload-file -C link-args=${src}@${dst}`;
}

// Cargo doesn't track flag changes: force our own crate to relink when
// the link inputs (flags, shell, preload set) change, so `prebuild` on
// every vite build stays a no-op instead of a minute-long relink.
const fingerprint = JSON.stringify({
	rustflags: env.RUSTFLAGS,
	shell: statSync(join(rootDir, "frontend/shell.html")).mtimeMs,
	preloads: preloads.map(([src]) => src),
	profile,
});
const fingerprintFile = join(rootDir, "tmp/frontend-fingerprint.json");
let prevFingerprint = "";
try {
	prevFingerprint = readFileSync(fingerprintFile, "utf8");
} catch {
	// First build.
}
if (prevFingerprint !== fingerprint) {
	// Cargo doesn't track flag changes and `clean -p` misses our outputs,
	// so drop them directly to force a relink with current flags.
	for (const file of [
		"khanqah-frontend.js",
		"khanqah_frontend.wasm",
		"khanqah-frontend.data",
	]) {
		try {
			unlinkSync(join(`frontend/target/${TARGET}/${profile}`, file));
		} catch {
			// Already absent.
		}
	}
	writeFileSync(fingerprintFile, fingerprint);
}

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
// emcc drops the preloaded-data bundle next to its intermediate link
// output (deps/), named after the crate: the loader fetches it relative
// to the page, so it must ship beside the .js under that exact name.
const dataArtifact = join(outDir, "deps/khanqah_frontend.data");
if (!existsSync(dataArtifact)) {
	console.error(`[frontend] expected artifact missing: ${dataArtifact}`);
	process.exit(1);
}
mkdirSync("public/game", { recursive: true });
copyFileSync(
	join(outDir, "khanqah-frontend.js"),
	"public/game/khanqah-frontend.js",
);
copyFileSync(
	join(outDir, "khanqah_frontend.wasm"),
	"public/game/khanqah_frontend.wasm",
);
copyFileSync(dataArtifact, "public/game/khanqah_frontend.data");
// The page entry is our shell template with the loader inlined where
// Emscripten would put {{{ SCRIPT }}} (cargo owns `-o`, so emcc never
// sees an .html output to template itself).
const shell = readFileSync(join(rootDir, "frontend/shell.html"), "utf8");
const MARKER = "{{{ SCRIPT }}}";
if (shell.split(MARKER).length !== 2) {
	console.error(
		"[frontend] shell template must contain {{{ SCRIPT }}} exactly once",
	);
	process.exit(1);
}
// Deploy version: content hash over loader + WASM + data, so every
// build gets a distinct cache key for all three fixed filenames.
const version = createHash("sha256")
	.update(readFileSync(join(outDir, "khanqah-frontend.js")))
	.update(readFileSync(join(outDir, "khanqah_frontend.wasm")))
	.update(readFileSync(dataArtifact))
	.digest("hex")
	.slice(0, 12);
if (!shell.includes("__FRONTEND_V__")) {
	console.error("[frontend] shell template lost its __FRONTEND_V__ marker");
	process.exit(1);
}
writeFileSync(
	"public/game/index.html",
	shell
		.replaceAll("__FRONTEND_V__", version)
		.replace(MARKER, `<script src="khanqah-frontend.js?v=${version}"></script>`),
);
console.log("[frontend] wrote public/game/index.html + .js + .wasm + .data");
