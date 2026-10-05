// Syntax check for plain-JS runtimes (server/, worker/, scripts/, tests/).
// Directories that do not exist yet (later phases) are skipped.
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOTS = ["server", "worker", "scripts", "tests"];

function collect(dir, out = []) {
	if (!existsSync(dir)) {
		return out;
	}
	for (const entry of readdirSync(dir)) {
		const full = join(dir, entry);
		if (statSync(full).isDirectory()) {
			collect(full, out);
		} else if (/\.(m|c)?js$/.test(entry)) {
			out.push(full);
		}
	}
	return out;
}

const files = ROOTS.flatMap((root) => collect(root));
if (files.length === 0) {
	console.log("[check] no JS files yet, nothing to check");
	process.exit(0);
}

let failed = false;
for (const file of files) {
	try {
		execFileSync(process.execPath, ["--check", file], { stdio: "pipe" });
	} catch {
		console.error(`[check] syntax error: ${file}`);
		failed = true;
	}
}
if (failed) {
	process.exit(1);
}
console.log(`[check] ${files.length} files OK`);
