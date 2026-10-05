// Builds the Rust WASM crates into public/wasm/ for Vite dev/build.
// Tolerant by design: if cargo or the wasm32 target is missing, it warns
// and skips so contributors without Rust can still work (the TS loaders
// degrade gracefully).
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";

const TARGET = "wasm32-unknown-unknown";
// NB: cargo converts dashes to underscores in output file names, and
// resolves target/ from the working directory, so build inside each crate.
const CRATES = [
	{
		dir: "wasm/signer",
		artifact: `wasm/signer/target/${TARGET}/release/khanqah_signer.wasm`,
		out: "public/wasm/signer.wasm",
	},
	{
		dir: "wasm/sim",
		artifact: `wasm/sim/target/${TARGET}/release/khanqah_sim.wasm`,
		out: "public/wasm/sim.wasm",
	},
];

function haveToolchain() {
	try {
		execFileSync("cargo", ["--version"], { stdio: "ignore" });
		const targets = execFileSync("rustup", ["target", "list", "--installed"], {
			encoding: "utf8",
		});
		return targets.split(/\r?\n/).includes(TARGET);
	} catch {
		return false;
	}
}

if (!haveToolchain()) {
	console.warn(
		`[wasm] cargo or the ${TARGET} target is missing, skipping WASM builds. ` +
			"Install Rust and run: rustup target add wasm32-unknown-unknown",
	);
	process.exit(0);
}

mkdirSync("public/wasm", { recursive: true });
for (const crate of CRATES) {
	execFileSync("cargo", ["build", "--release", "--lib", "--target", TARGET], {
		stdio: "inherit",
		cwd: crate.dir,
	});
	if (!existsSync(crate.artifact)) {
		console.error(`[wasm] expected artifact missing: ${crate.artifact}`);
		process.exit(1);
	}
	copyFileSync(crate.artifact, crate.out);
	console.log(`[wasm] wrote ${crate.out}`);
}
