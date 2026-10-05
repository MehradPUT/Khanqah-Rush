import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

// Guards the legacy-bundle entry wiring on the upstream base. Extended
// with keycode and envelope assertions in the integration phase.
const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");

describe("legacy entry smoke", () => {
	it("exposes the documented npm scripts", () => {
		const pkg = JSON.parse(read("package.json"));
		for (const script of [
			"dev",
			"build",
			"preview",
			"test",
			"check",
			"lint",
			"format",
		]) {
			expect(pkg.scripts[script], script).toBeTruthy();
		}
	});

	it("loads the legacy bundle from index.html", () => {
		expect(read("index.html")).toContain("js/main.js");
		expect(fs.existsSync(path.join(root, "public/js/main.js"))).toBe(true);
	});
});
