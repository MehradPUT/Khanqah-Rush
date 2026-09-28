import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { beforeEach, describe, expect, it } from "vitest";

// Dummy fixtures so tests run offline. Set real values via .env for live bot runs.
const TEST_BOT_TOKEN =
	process.env.TELEGRAM_BOT_TOKEN || "DUMMY_TOKEN_FOR_TESTS";
const TEST_CHAT_ID = Number(process.env.TELEGRAM_CHAT_ID) || -100123456789;

function setupGlobals() {
	delete global.window;
	global.window = {
		Telegram: {
			WebApp: {
				initDataUnsafe: {
					user: { first_name: "نیما", username: "nimak" },
					chat: { id: TEST_CHAT_ID },
				},
				sendData: () => {},
			},
		},
		KHANQAH_CONFIG: {
			botToken: TEST_BOT_TOKEN,
			chatId: TEST_CHAT_ID,
			reportUrl: "/api/testScore",
		},
	};
	global.fetch = async () => ({ ok: true, json: async () => ({ ok: true }) });
	globalThis.ca = 0;
	globalThis.Fa = () => {};
	globalThis.R =
		"eyJuIjoiTmltYSBLIiwiY2kiOi0xMDAxMjM0NTY3ODl9MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=";
	globalThis.Ba = "نیما";
}

function loadAnticheatSlice() {
	const file = path.join(process.cwd(), "public/js/main.js");
	const src = fs.readFileSync(file, "utf8").replace(/\r\n/g, "\n");
	const startMarker =
		"// ==========================================\n// ANTI-CHEAT HONEYPOT SENSORS & CONSOLE BAIT";
	const endMarker = "window.KhanqahAntiCheat = {";
	const start = src.indexOf(startMarker);
	const endPos = src.indexOf(endMarker);
	if (start === -1 || endPos === -1) {
		throw new Error(
			"Could not locate anti-cheat code slice in public/js/main.js",
		);
	}
	const end = src.indexOf("};", endPos) + 2;
	vm.runInThisContext(src.slice(start, end), {
		filename: "anticheat-slice.js",
	});
}

beforeEach(() => {
	setupGlobals();
	loadAnticheatSlice();
});

describe("anticheat honeypot slice", () => {
	it("starts clean with decoy APIs exposed", () => {
		expect(typeof window.setScore).toBe("function");
		expect(typeof window.Lumberjack.setScore).toBe("function");
		expect(typeof window.KhanqahAntiCheat).toBe("object");
		expect(window.KhanqahAntiCheat.isCheater()).toBe(false);
	});

	it("traps console assignment window.score = 100", () => {
		window.score = 100;
		expect(window.score).toBe(100);
		expect(window.KhanqahAntiCheat.isCheater()).toBe(true);
		expect(window.KhanqahAntiCheat.getReason()).toBe(
			"console_score_assignment",
		);
	});

	it("traps window.setScore({ score: 100 })", () => {
		window.setScore({ score: 100 });
		expect(window.score).toBe(100);
		expect(window.KhanqahAntiCheat.isCheater()).toBe(true);
		expect(window.KhanqahAntiCheat.getReason()).toBe("window_setScore");
	});

	it("resolves player name from Ba first", () => {
		const name = globalThis.getPlayerDisplayName();
		expect(name).toBe("نیما");
	});
});
