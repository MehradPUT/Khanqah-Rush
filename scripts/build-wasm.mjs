// Builds wasm/signer to public/wasm/signer.wasm for Vite dev/build.
// Tolerant by design during the stub phase: if cargo or the wasm32 target
// is missing, it warns and skips so contributors without Rust can still
// work (the TS loader degrades gracefully). The signed-score task will
// make this step required.
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";

const TARGET = "wasm32-unknown-unknown";
// NB: cargo converts dashes to underscores in output file names.
const ARTIFACT =
	"wasm/signer/target/wasm32-unknown-unknown/release/khanqah_signer.wasm";
const OUT = "public/wasm/signer.wasm";

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
		`[wasm] cargo or the ${TARGET} target is missing, skipping signer build. ` +
			"Install Rust and run: rustup target add wasm32-unknown-unknown",
	);
	process.exit(0);
}

execFileSync("cargo", ["build", "--release", "--target", TARGET], {
	stdio: "inherit",
	// NB: cargo resolves target/ from the working directory, not from
	// --manifest-path, so run inside the crate to keep target/ local.
	cwd: "wasm/signer",
});

if (!existsSync(ARTIFACT)) {
	console.error(`[wasm] expected artifact missing: ${ARTIFACT}`);
	process.exit(1);
}

mkdirSync("public/wasm", { recursive: true });
copyFileSync(ARTIFACT, OUT);
console.log(`[wasm] wrote ${OUT}`);
