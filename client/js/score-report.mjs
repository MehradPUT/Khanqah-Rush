/**
 * Companion score reporter for the legacy bundle game.
 *
 * The minified bundle cannot be safely rewired, so this script observes
 * from the outside instead of patching the submitter:
 * - chop inputs via its own key/touch listeners, gated on `#page_wrap`
 *   carrying `in_game` (menu typing is never recorded),
 * - round state via `#page_wrap.in_result` plus `window.score` *reads*
 *   (trap-free; only *writes* trip the honeypot),
 * - trace packed binary (shared codec, raw + base64 — no CompressionStream:
 *   several mobile browsers never resolve it), hashed into a v2
 *   envelope signed in WASM, POSTed same-origin on game over.
 *
 * Runs only with launch params (`lt`, `sid`, `sk`, `seed`) issued by the
 * bot server; otherwise the game stays local-only. Silent by design.
 */
import {
	HERO_NIMA,
	heroIdForName,
	packTrace,
	sha256Hex,
	splitSeedHex,
	traceToB64,
} from "../../shared/trace-codec.js";
import { loadSigner } from "./signer-loader.mjs";

const POLL_MS = 500;
const HEX_64 = /^[0-9a-f]{64}$/;
const HEX_16 = /^[0-9a-f]{16}$/;

// Debug instrumentation is deploy-gated: players get a silent
// companion (no badge, no console output) while developers append
// `&dbg=1` to the game URL for the full trace. Never logs secrets
// (key/token/tag/trace) in either mode.
const DEBUG = (() => {
	try {
		return new URLSearchParams(window.location.search).has("dbg");
	} catch {
		return false;
	}
})();

function dlog(...args) {
	try {
		if (DEBUG) {
			console.log("[khanqah-debug]", ...args);
		}
	} catch {
		// Logging must never disturb the game.
	}
}

function wrapClasses() {
	try {
		return document.getElementById("page_wrap")?.className ?? "<no page_wrap>";
	} catch {
		return "<unreadable>";
	}
}

/** Selected hero id for the trace (Nima when unreadable). */
function readHero() {
	try {
		return heroIdForName(window.khanqahGame?.getCharacter?.());
	} catch {
		return HERO_NIMA;
	}
}

/**
 * True while the bundle ignores chop inputs but the round goes on:
 * Ali's auto-flurry, Parsa's nap, Fargol's sacrifice cinematic. Inputs
 * here must not enter the trace, or replay diverges. Each flag is read
 * synchronously per input, so companion and bundle always agree.
 */
function inputIgnored() {
	try {
		const game = window.khanqahGame;
		if (!game) {
			return false;
		}
		return !!(
			game.isAliFlurryActive?.() ||
			game.isParsaSleeping?.() ||
			game.isFargolSacrificeInProgress?.()
		);
	} catch {
		return false;
	}
}

// Signer warmed at page load, not at game over: fetching +
// instantiating after death delays submission (and a quickly closed
// tab would lose the score entirely). The module is 10 KB and the key
// comes from the launch URL, so by report time this is resolved.
let signerPromise = null;

function warmSigner(launch) {
	if (!signerPromise) {
		dlog("warming signer");
		signerPromise = loadSigner()
			.then((signer) => {
				if (signer?.setSessionKey(launch.key)) {
					dlog("signer warm");
					return signer;
				}
				dlog("signer warm failed");
				return null;
			})
			.catch(() => {
				dlog("signer warm failed");
				return null;
			});
	}
	return signerPromise;
}

// Reject if a stage stalls (mobile browsers can suspend work when the
// tab loses focus); turns silent hangs into visible stage failures.
function withTimeout(promise, ms, label) {
	return Promise.race([
		promise,
		new Promise((_, reject) => {
			setTimeout(() => reject(new Error(`timeout:${label}`)), ms);
		}),
	]);
}

// Resolve the warmed signer, with one fresh retry if warming stalled
// (mobile browsers suspend background-tab work unpredictably).
async function readySigner(launch) {
	const warmed = await withTimeout(warmSigner(launch), 5000, "load-signer");
	if (warmed) {
		return warmed;
	}
	dlog("signer retry");
	return withTimeout(
		loadSigner()
			.then((signer) => {
				if (signer?.setSessionKey(launch.key)) {
					return signer;
				}
				return null;
			})
			.catch(() => null),
		8000,
		"load-signer-retry",
	);
}

function readLaunch() {
	const params = new URLSearchParams(window.location.search);
	const launchToken = params.get("lt");
	const sessionId = params.get("sid");
	const sessionKeyHex = params.get("sk");
	const seedHex = params.get("seed");
	if (
		!launchToken ||
		!sessionId ||
		!sessionKeyHex ||
		!HEX_64.test(sessionKeyHex) ||
		!seedHex ||
		!HEX_16.test(seedHex)
	) {
		return null;
	}
	const key = new Uint8Array(32);
	for (let i = 0; i < 32; i++) {
		key[i] = Number.parseInt(sessionKeyHex.slice(i * 2, i * 2 + 2), 16);
	}
	const seed = splitSeedHex(seedHex);
	if (!seed) {
		return null;
	}
	return { launchToken, sessionId, key, seed };
}

function currentScore() {
	const score = Number(window.score);
	return Number.isInteger(score) && score > 0 ? score : 0;
}

function inGame() {
	return (
		document.getElementById("page_wrap")?.classList.contains("in_game") ?? false
	);
}

function gameOver() {
	return (
		document.getElementById("page_wrap")?.classList.contains("in_result") ??
		false
	);
}

const BADGE_ID = "khanqah-save-badge";

function badge() {
	let el = document.getElementById(BADGE_ID);
	if (!el) {
		el = document.createElement("div");
		el.id = BADGE_ID;
		el.style.cssText =
			"position:fixed;left:50%;bottom:12px;transform:translateX(-50%);" +
			"z-index:9999;pointer-events:none;font:700 12px system-ui,sans-serif;" +
			"padding:4px 12px;border-radius:999px;display:none;color:#fff;";
		document.body.appendChild(el);
	}
	return el;
}

let badgeTimer = 0;

function showBadge(text, background, sticky = false) {
	if (!DEBUG) {
		return;
	}
	try {
		const el = badge();
		el.textContent = text;
		el.style.background = background;
		el.style.display = "block";
		if (badgeTimer) {
			clearTimeout(badgeTimer);
			badgeTimer = 0;
		}
		if (!sticky) {
			badgeTimer = window.setTimeout(() => {
				el.style.display = "none";
			}, 5000);
		}
	} catch {
		// Badge must never disturb the game.
	}
}

function hideBadge() {
	if (!DEBUG) {
		return;
	}
	try {
		const el = document.getElementById(BADGE_ID);
		if (el) {
			el.style.display = "none";
		}
	} catch {
		// Ignore.
	}
}

async function reportOnce(launch, score, durationSec, chops, endTimeMs, hero) {
	// Resolves "verdict" once the server answered (saved/rejected) or the
	// failure is permanent; "retry" when no verdict was reached (network
	// down, stalled stage) and the poll may try once more.
	const fail = (stage, detail) => {
		dlog("report failed", {
			stage,
			detail: detail ?? null,
			score,
			chops: chops.length,
		});
		window.__khanqah.lastReport = detail ? `${stage}: ${detail}` : stage;
		showBadge(`✗ ${stage}`, "#b91c1c");
	};
	dlog("reportOnce start", {
		score,
		durationSec,
		chops: chops.length,
		endTimeMs,
		hero,
		classes: wrapClasses(),
	});
	try {
		const signer = await readySigner(launch);
		dlog("report stage: signer ready", { ok: !!signer });
		if (!signer) {
			fail("signer-missing");
			return "verdict";
		}
		const raw = packTrace({
			hero,
			seedLo: launch.seed.seedLo,
			seedHi: launch.seed.seedHi,
			chops,
			endTimeMs,
		});
		if (!raw) {
			fail("pack-failed");
			return "verdict";
		}
		dlog("report stage: packed", { bytes: raw.length });
		const trace = traceToB64(raw);
		const traceHash = await withTimeout(
			sha256Hex(raw).catch(() => null),
			15000,
			"hash",
		);
		if (!traceHash) {
			fail("hash-failed");
			return "verdict";
		}
		const nonceBytes = crypto.getRandomValues(new Uint8Array(16));
		const nonce = Array.from(nonceBytes)
			.map((b) => b.toString(16).padStart(2, "0"))
			.join("");
		const timestamp = Math.floor(Date.now() / 1000);
		const tag = signer.signEnvelope({
			sessionId: launch.sessionId,
			score,
			durationSec,
			nonce,
			timestamp,
			traceHash,
		});
		if (!tag) {
			fail("no-tag");
			return "verdict";
		}
		let recorded = false;
		let netError = false;
		let httpStatus = 0;
		let debugReason = null;
		try {
			dlog("report stage: post");
			const res = await withTimeout(
				fetch("/api/setScore", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						lt: launch.launchToken,
						sid: launch.sessionId,
						score,
						durationSec,
						nonce,
						timestamp,
						tag,
						trace,
						traceHash,
					}),
				}),
				20000,
				"post",
			);
			httpStatus = res.status;
			const body = await res.json().catch(() => ({}));
			recorded = !!body?.recorded;
			// TEMP-DEBUG: surface the server's reject reason until verified.
			debugReason =
				typeof body?.debugReason === "string" ? body.debugReason : null;
		} catch (err) {
			netError = true;
			dlog("report POST error", {
				message: err instanceof Error ? err.message : String(err),
			});
		}
		dlog("report POST done", {
			score,
			chops: chops.length,
			endTimeMs,
			httpStatus,
			recorded,
			debugReason,
			netError,
		});
		if (netError) {
			fail("net-error");
			return "retry";
		}
		window.__khanqah.lastReport = recorded
			? "saved"
			: (debugReason ?? "rejected");
		showBadge(
			recorded ? "✓ score saved" : `✗ ${debugReason ?? "not recorded"}`,
			recorded ? "#15803d" : "#b91c1c",
		);
		return "verdict";
	} catch (err) {
		const message = err instanceof Error ? err.message : String(err);
		fail("error", message);
		// Stalled stages (timeouts) are transient; anything else stands.
		return message.startsWith("timeout:") ? "retry" : "verdict";
	}
}

function watch() {
	const launch = readLaunch();
	window.__khanqah = {
		hasLaunch: !!launch,
		recording: false,
		lastReport: "none",
		chops: 0,
		lastPoll: null,
	};
	dlog("watch init", { hasLaunch: !!launch, classes: wrapClasses() });
	if (!launch) {
		return;
	}
	// Warm the signer while the page loads so reporting after game over
	// never waits on fetch + instantiation.
	warmSigner(launch);
	let roundStart = null;
	let reported = false;
	let chops = [];
	let hero = HERO_NIMA;
	// Frozen finished round awaiting the poll's report. The bundle drops
	// `in_game` and raises `in_result` in the same synchronous block, so
	// the observer must freeze — never wipe — a round that just ended;
	// otherwise the poll finds empty hands and skips the report.
	let pending = null;
	let overLogged = false;
	let skipLogged = false;
	// Bounded retries: a report with no server verdict (network down,
	// stalled stage) may try once more; a verdict (saved/rejected) never
	// reposts. Reset every round.
	let attempts = 0;
	// Pre-round stream reset: capture-phase listeners run before the
	// bundle's own handlers in the same user gesture, so the seeded stream
	// restarts ahead of the round-init draws. Poll-based reset would come
	// up to 500 ms too late (after the draws already consumed stream).
	const primeStream = () => {
		try {
			if (!inGame() && typeof window.__rngReset === "function") {
				window.__rngReset();
			}
		} catch {
			// Reset is best-effort; the trace still records.
		}
	};
	window.addEventListener("keydown", primeStream, true);
	window.addEventListener("pointerdown", primeStream, true);
	// Round transitions via MutationObserver: near-zero delay, so chops
	// landing between transition and the next poll tick are still caught.
	// (Sub-frame machine-speed inputs remain a known residual.)
	const syncRoundState = () => {
		try {
			if (inGame() && !gameOver()) {
				if (roundStart === null) {
					// Stream already reset by the primer; never reset here.
					roundStart = Date.now();
					chops = [];
					hero = readHero();
					pending = null;
					dlog("round start seen", { classes: wrapClasses(), hero });
				}
			} else if (gameOver()) {
				if (roundStart !== null) {
					pending = { chops, roundStart, hero };
					dlog("round frozen for report", {
						classes: wrapClasses(),
						chops: chops.length,
						score: currentScore(),
					});
					roundStart = null;
					chops = [];
				}
			} else if (!inGame()) {
				// Menu without a result (mid-round quit): nothing to report.
				if (roundStart !== null || pending !== null) {
					dlog("round discarded (menu, no result)", {
						classes: wrapClasses(),
						chops: chops.length,
					});
				}
				roundStart = null;
				chops = [];
				pending = null;
			}
		} catch {
			// Observer must never disturb the game.
		}
	};
	const wrap = document.getElementById("page_wrap");
	if (wrap && typeof MutationObserver !== "undefined") {
		new MutationObserver(syncRoundState).observe(wrap, {
			attributes: true,
			attributeFilter: ["class"],
		});
	}
	const record = (side) => {
		try {
			if (roundStart === null || !inGame() || gameOver() || inputIgnored()) {
				return;
			}
			chops.push({ side, t: Date.now() - roundStart });
		} catch {
			// Observer must never disturb the game.
		}
	};
	// Capture phase (like the primer): record the input before the
	// bundle's own handlers run, so even a lethal chop that ends the
	// round synchronously is still in the trace. The gameOver() gate
	// stays as second-line defence.
	window.addEventListener(
		"keydown",
		(e) => {
			const code = e.code;
			if (code === "ArrowLeft" || code === "KeyA" || code === "KeyH") {
				record(0);
			} else if (code === "ArrowRight" || code === "KeyD" || code === "KeyL") {
				record(1);
			}
		},
		true,
	);
	window.addEventListener(
		"pointerdown",
		(e) => {
			try {
				const target = e.target instanceof Element ? e.target : null;
				if (!target) {
					return;
				}
				if (target.closest("#button_left")) {
					record(0);
				} else if (target.closest("#button_right")) {
					record(1);
				}
			} catch {
				// Observer must never disturb the game.
			}
		},
		true,
	);
	setInterval(() => {
		try {
			const score = currentScore();
			const ig = inGame();
			const over = gameOver();
			window.__khanqah.lastPoll = {
				inGame: ig,
				gameOver: over,
				score,
				chops: chops.length,
				roundActive: roundStart !== null,
				hasPending: pending !== null,
				reported,
				classes: wrapClasses(),
			};
			if (ig && !over) {
				syncRoundState();
				reported = false;
				overLogged = false;
				skipLogged = false;
				attempts = 0;
				window.__khanqah.recording = true;
				window.__khanqah.chops = chops.length;
				showBadge("● REC", "#b45309", true);
				return;
			}
			if (over && !overLogged) {
				overLogged = true;
				dlog("game over seen", {
					score,
					chops: chops.length,
					roundActive: roundStart !== null,
					hasPending: pending !== null,
					reported,
					classes: wrapClasses(),
				});
			}
			window.__khanqah.recording = false;
			if (score === 0 && !gameOver()) {
				// Idle menu: result gone, score reset — drop everything.
				// (While the result screen still shows, a 0 read is
				// transient: keep a frozen pending report.)
				roundStart = null;
				chops = [];
				pending = null;
				hideBadge();
			}
			// Prefer live data (observer may not have run yet); fall back
			// to the frozen round.
			const src = roundStart !== null ? { chops, roundStart, hero } : pending;
			if (
				score > 0 &&
				gameOver() &&
				!reported &&
				attempts < 2 &&
				src !== null &&
				src.roundStart !== null
			) {
				attempts += 1;
				reported = true;
				pending = null;
				const endTimeMs = Date.now() - src.roundStart;
				const durationSec = Math.max(1, Math.round(endTimeMs / 1000));
				dlog("firing report", {
					score,
					durationSec,
					chops: src.chops.length,
					endTimeMs,
					attempt: attempts,
					hero: src.hero,
				});
				void reportOnce(
					launch,
					score,
					durationSec,
					src.chops,
					endTimeMs,
					src.hero,
				).then((outcome) => {
					// No verdict (network down, stalled stage): restore the
					// round for one more attempt while the result screen
					// is still up. A verdict never reposts.
					if (outcome === "retry" && attempts < 2) {
						pending = {
							chops: src.chops,
							roundStart: src.roundStart,
							hero: src.hero,
						};
						reported = false;
						skipLogged = false;
						dlog("report will retry", { attempts });
					}
				});
				roundStart = null;
				chops = [];
			} else if (gameOver() && !reported && !skipLogged) {
				skipLogged = true;
				dlog("report skipped", { score, hasPending: pending !== null });
			}
		} catch {
			// Observer must never disturb the game.
		}
	}, POLL_MS);
}

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", watch, { once: true });
} else {
	watch();
}
