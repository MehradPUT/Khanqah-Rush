import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

// Guards the legacy-bundle entry wiring on the upstream base.
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

	it("binds H/L vim keys in gameplay and menu", () => {
		const bundle = read("public/js/main.js");
		expect(bundle).toContain("(37==a||72==a)&&(Ka(La),Ca(!0))");
		expect(bundle).toContain("(39==a||76==a)&&(Ka(jb),Ca(!1))");
		// Menu carousel follows the same keys.
		expect(bundle).toContain("(37==a||72==a)?rotateCharacter(-1)");
		expect(bundle).toContain("(39==a||76==a)?rotateCharacter(1)");
	});

	it("keeps public/ and dist/ bundles identical", () => {
		expect(read("public/js/main.js")).toBe(read("dist/js/main.js"));
	});

	it("wires the signed-report companion without bundle surgery", () => {
		expect(read("index.html")).toContain("/client/js/score-report.mjs");
		const reporter = read("client/js/score-report.mjs");
		expect(reporter).toContain("in_result");
		expect(reporter).toContain("/api/setScore");
		expect(reporter).toContain("signer-loader.mjs");
		expect(reporter).not.toContain("TELEGRAM_BOT_TOKEN");
	});
});
