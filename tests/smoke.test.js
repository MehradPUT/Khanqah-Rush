import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

// Placeholder suite guarding repo invariants after the client honeypot
// anti-cheat was removed (see docs/anticheat-future.md). Keeps `npm test`
// green until real game-logic tests land with the Vite/WASM migration.
const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");

describe("project smoke", () => {
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

	it("ignores local-only paths", () => {
		const ignore = read(".gitignore").replace(/\r\n/g, "\n");
		for (const entry of ["node_modules/", "dist/", "scratch/", ".env"]) {
			expect(ignore).toContain(entry);
		}
	});

	it("keeps the frozen legacy entry wiring", () => {
		expect(read("index.html")).toContain("js/main.js");
		expect(fs.existsSync(path.join(root, "public/js/main.js"))).toBe(true);
	});

	it("keeps the anti-cheat follow-up note", () => {
		expect(fs.existsSync(path.join(root, "docs/anticheat-future.md"))).toBe(
			true,
		);
	});
});
