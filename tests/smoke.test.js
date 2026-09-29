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

	it("wires the Vite entry and required DOM hooks", () => {
		const html = read("index.html").replace(/\r\n/g, "\n");
		expect(html).toContain("/src/main.ts");
		expect(html).not.toContain("js/main.js");
		for (const id of [
			"gameCanvas",
			"hud",
			"scoreDisplay",
			"bestScoreDisplay",
			"staminaFill",
			"abilityIndicator",
			"phaseAvatar",
			"phaseTag",
			"gaugeTitle",
			"gaugeTime",
			"gaugeFill",
			"vfxOverlay",
			"startMenu",
			"gameOverMenu",
			"btnChopLeft",
			"btnChopRight",
			"btnStartGame",
			"btnPlayAgain",
			"btnShareTelegram",
			"btnToggleSound",
			"btnToggleVoice",
			"soundIcon",
			"soundStatus",
			"voiceIcon",
			"voiceStatus",
			"finalScore",
			"finalSurvivalTime",
			"finalRejuvenationCount",
			"bestScoreFinal",
			"defeatSpeech",
			"voiceSubtitle",
			"speechText",
		]) {
			expect(html, id).toContain(`id="${id}"`);
		}
	});

	it("keeps the anti-cheat follow-up note", () => {
		expect(fs.existsSync(path.join(root, "docs/anticheat-future.md"))).toBe(
			true,
		);
	});

	it("keeps the reference bot server", () => {
		expect(fs.existsSync(path.join(root, "server/example.cjs"))).toBe(true);
	});
});
