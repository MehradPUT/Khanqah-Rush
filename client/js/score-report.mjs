/**
 * Companion score reporter for the legacy bundle game.
 *
 * The minified bundle cannot be safely rewired, so this script observes
 * from the outside instead of patching the submitter:
 * - chop inputs via its own key/touch listeners, gated on `#page_wrap`
 *   carrying `in_game` (menu typing is never recorded),
 * - round state via `#page_wrap.in_result` plus `window.score` *reads*
 *   (trap-free; only *writes* trip the honeypot),
 * - trace packed binary + deflated (shared codec), hashed into a v2
 *   envelope signed in WASM, POSTed same-origin on game over.
 *
 * Runs only with launch params (`lt`, `sid`, `sk`, `seed`) issued by the
 * bot server; otherwise the game stays local-only. Silent by design.
 */
import {
	deflateTrace,
	packTrace,
	sha256Hex,
	splitSeedHex,
} from "../../shared/trace-codec.js";
import { loadSigner } from "./signer-loader.mjs";

const POLL_MS = 500;
const HEX_64 = /^[0-9a-f]{64}$/;
const HEX_16 = /^[0-9a-f]{16}$/;

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
	try {
		const el = document.getElementById(BADGE_ID);
		if (el) {
			el.style.display = "none";
		}
	} catch {
		// Ignore.
	}
}

async function reportOnce(launch, score, durationSec, chops, endTimeMs) {
	const fail = (stage, detail) => {
		window.__khanqah.lastReport = detail ? `${stage}: ${detail}` : stage;
		showBadge(`✗ ${stage}`, "#b91c1c");
	};
	try {
		const signer = await loadSigner().catch(() => null);
		if (!signer) {
			fail("signer-missing");
			return;
		}
		if (!signer.setSessionKey(launch.key)) {
			fail("session-key");
			return;
		}
		const raw = packTrace({
			seedLo: launch.seed.seedLo,
			seedHi: launch.seed.seedHi,
			chops,
			endTimeMs,
		});
		if (!raw) {
			fail("pack-failed");
			return;
		}
		const traceBytes = await deflateTrace(raw).catch(() => null);
		if (!traceBytes) {
			fail("deflate-failed");
			return;
		}
		const trace = btoa(
			Array.from(traceBytes)
				.map((b) => String.fromCharCode(b))
				.join(""),
		);
		const traceHash = await sha256Hex(traceBytes).catch(() => null);
		if (!traceHash) {
			fail("hash-failed");
			return;
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
			return;
		}
		let recorded = false;
		let netError = false;
		try {
			const res = await fetch("/api/setScore", {
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
			});
			recorded = !!(await res.json().catch(() => ({})))?.recorded;
		} catch {
			netError = true;
		}
		if (netError) {
			fail("net-error");
			return;
		}
		window.__khanqah.lastReport = recorded ? "saved" : "rejected";
		showBadge(
			recorded ? "✓ score saved" : "✗ not recorded",
			recorded ? "#15803d" : "#b91c1c",
		);
	} catch (err) {
		fail("error", err instanceof Error ? err.message : String(err));
	}
}

function watch() {
	const launch = readLaunch();
	window.__khanqah = {
		hasLaunch: !!launch,
		recording: false,
		lastReport: "none",
		chops: 0,
	};
	if (!launch) {
		return;
	}
	let roundStart = null;
	let reported = false;
	let chops = [];
	const record = (side) => {
		try {
			if (roundStart === null || !inGame() || gameOver()) {
				return;
			}
			chops.push({ side, t: Date.now() - roundStart });
		} catch {
			// Observer must never disturb the game.
		}
	};
	window.addEventListener("keydown", (e) => {
		const code = e.code;
		if (code === "ArrowLeft" || code === "KeyA" || code === "KeyH") {
			record(0);
		} else if (code === "ArrowRight" || code === "KeyD" || code === "KeyL") {
			record(1);
		}
	});
	for (const [id, side] of [
		["button_left", 0],
		["button_right", 1],
	]) {
		document
			.getElementById(id)
			?.addEventListener("pointerdown", () => record(side));
	}
	setInterval(() => {
		try {
			const score = currentScore();
			if (inGame() && !gameOver()) {
				if (roundStart === null) {
					roundStart = Date.now();
					chops = [];
				}
				reported = false;
				window.__khanqah.recording = true;
				window.__khanqah.chops = chops.length;
				showBadge("● REC", "#b45309", true);
				return;
			}
			window.__khanqah.recording = false;
			if (score === 0) {
				roundStart = null;
				chops = [];
				hideBadge();
			}
			if (score > 0 && gameOver() && !reported && roundStart !== null) {
				reported = true;
				const endTimeMs = Date.now() - roundStart;
				const durationSec = Math.max(1, Math.round(endTimeMs / 1000));
				void reportOnce(launch, score, durationSec, chops, endTimeMs).catch(
					() => {},
				);
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
