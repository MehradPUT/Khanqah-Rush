import { readFile } from "node:fs/promises";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { HERO_FARGOL, unpackTrace } from "../shared/trace-codec.js";

// Real harness for the legacy-page companion (client/js/score-report.mjs).
// DOM is stubbed lightly (no jsdom): class sets drive in_game/in_result,
// captured listeners stand in for input, fetch serves the real signer.wasm
// bytes and records score posts. MutationObserver stays undefined (the
// module skips it via typeof guard), so the poll path is exercised.
describe("companion score reporter", () => {
	let classes;
	let listeners;
	let intervalCb;
	let badge;
	let posts;
	let win;
	let signerBytes;

	function setClasses(...names) {
		classes = new Set(names);
	}

	function tick() {
		intervalCb();
	}

	function keydown(code) {
		for (const fn of listeners.keydown) {
			fn({ code });
		}
	}

	function pointerdown(target) {
		for (const fn of listeners.pointerdown) {
			fn({ target });
		}
	}

	async function flush(ms = 100) {
		await new Promise((resolve) => setTimeout(resolve, ms));
	}

	function lastPostBody() {
		expect(posts.length).toBeGreaterThan(0);
		return JSON.parse(posts[posts.length - 1][1].body);
	}

	beforeAll(async () => {
		signerBytes = await readFile("public/wasm/signer.wasm").catch(() => null);
		if (!signerBytes) {
			return;
		}
		setClasses("page_wrap", "loading", "in_result", "in_greet");
		listeners = { keydown: [], pointerdown: [] };
		posts = [];
		win = {
			location: {
				search:
					"?lt=tok&sid=sid-harness&sk=" +
					"ab".repeat(32) +
					"&seed=" +
					"cd".repeat(8),
			},
			score: 0,
			addEventListener: (type, fn) => {
				listeners[type].push(fn);
			},
			setTimeout: (fn, ms) => setTimeout(fn, ms),
			clearTimeout: (id) => clearTimeout(id),
		};
		const documentStub = {
			readyState: "complete",
			getElementById: (id) => {
				if (id === "page_wrap") {
					return { classList: { contains: (c) => classes.has(c) } };
				}
				return null;
			},
			createElement: () => {
				badge = { style: {}, textContent: "" };
				return badge;
			},
			body: { appendChild: () => {} },
			addEventListener: () => {},
		};
		vi.stubGlobal("window", win);
		vi.stubGlobal("document", documentStub);
		vi.stubGlobal("setInterval", (fn) => {
			intervalCb = fn;
			return 1;
		});
		vi.stubGlobal("Element", class Element {});
		vi.stubGlobal("fetch", async (url, init) => {
			const href = String(url);
			if (href.endsWith("wasm/signer.wasm")) {
				return new Response(signerBytes, { status: 200 });
			}
			if (href.endsWith("/api/setScore")) {
				posts.push([href, init]);
				return new Response(JSON.stringify({ ok: true, recorded: true }), {
					status: 200,
				});
			}
			throw new Error(`unexpected fetch: ${href}`);
		});
		await import("../client/js/score-report.mjs");
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it("records keyboard chops and posts a signed trace on game over", async () => {
		if (!signerBytes) {
			return;
		}
		setClasses("page_wrap", "ready", "in_game");
		tick();
		expect(win.__khanqah.hasLaunch).toBe(true);
		expect(win.__khanqah.recording).toBe(true);

		keydown("ArrowLeft");
		keydown("KeyA");
		keydown("KeyH");
		expect(win.__khanqah.chops).toBe(0); // updated on next poll tick
		tick();
		expect(win.__khanqah.chops).toBe(3);

		win.score = 3;
		setClasses("page_wrap", "ready", "in_greet", "in_result");
		tick();
		await flush();

		const body = lastPostBody();
		expect(body.score).toBe(3);
		expect(body.sid).toBe("sid-harness");
		const trace = unpackTrace(
			Uint8Array.from(Buffer.from(body.trace, "base64")),
		);
		expect(trace.chops.map((c) => c.side)).toEqual([0, 0, 0]);
		expect(trace.chops.length).toBe(3);
		expect(win.__khanqah.lastReport).toBe("saved");
		expect(badge.textContent).toBe("✓ score saved");
	});

	it("skips scoreless game overs without posting", async () => {
		if (!signerBytes) {
			return;
		}
		const sent = posts.length;
		setClasses("page_wrap", "ready", "in_game");
		win.score = 0;
		tick();
		setClasses("page_wrap", "ready", "in_greet", "in_result");
		tick();
		await flush();
		expect(posts.length).toBe(sent);
	});

	it("records touch-button chops via capture listeners", async () => {
		if (!signerBytes) {
			return;
		}
		setClasses("page_wrap", "ready", "in_game");
		win.score = 0;
		tick();
		const target = new globalThis.Element();
		target.closest = (sel) => (sel === "#button_right" ? {} : null);
		pointerdown(target);
		tick();
		expect(win.__khanqah.chops).toBe(1);

		win.score = 1;
		setClasses("page_wrap", "ready", "in_greet", "in_result");
		tick();
		await flush();

		const body = lastPostBody();
		const trace = unpackTrace(
			Uint8Array.from(Buffer.from(body.trace, "base64")),
		);
		expect(trace.chops.map((c) => c.side)).toEqual([1]);
		expect(win.__khanqah.lastReport).toBe("saved");
	});

	it("tags the trace with the selected hero", async () => {
		if (!signerBytes) {
			return;
		}
		win.khanqahGame = { getCharacter: () => "fargol" };
		setClasses("page_wrap", "ready", "in_game");
		win.score = 0;
		tick();
		keydown("ArrowLeft");
		win.score = 1;
		setClasses("page_wrap", "ready", "in_greet", "in_result");
		tick();
		await flush();

		const body = lastPostBody();
		const trace = unpackTrace(
			Uint8Array.from(Buffer.from(body.trace, "base64")),
		);
		expect(trace.hero).toBe(HERO_FARGOL);
		win.khanqahGame = undefined;
	});

	it("drops inputs the bundle ignores (flurry, nap, sacrifice)", async () => {
		if (!signerBytes) {
			return;
		}
		const sent = posts.length;
		setClasses("page_wrap", "ready", "in_game");
		win.score = 0;
		tick();
		win.khanqahGame = { isAliFlurryActive: () => true };
		keydown("ArrowLeft");
		keydown("ArrowRight");
		tick();
		expect(win.__khanqah.chops).toBe(0);
		win.khanqahGame = { isParsaSleeping: () => true };
		keydown("ArrowLeft");
		tick();
		expect(win.__khanqah.chops).toBe(0);
		win.khanqahGame = { isFargolSacrificeInProgress: () => true };
		keydown("ArrowLeft");
		tick();
		expect(win.__khanqah.chops).toBe(0);
		win.khanqahGame = undefined;
		// Scoreless game over posts nothing.
		setClasses("page_wrap", "ready", "in_greet", "in_result");
		tick();
		await flush();
		expect(posts.length).toBe(sent);
	});
});
