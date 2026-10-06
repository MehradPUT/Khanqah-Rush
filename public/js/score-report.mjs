/**
 * Companion score reporter for the legacy bundle game.
 *
 * The minified bundle cannot be safely rewired, so this script observes
 * from the outside instead of patching the submitter:
 * - round state via `#page_wrap.in_result` (toggled by the bundle) and
 *   `window.score` *reads* (trap-free; only *writes* trip the honeypot),
 * - round duration measured from the first non-zero score,
 * - WASM-signed envelope POSTed same-origin on game over.
 *
 * Runs only with launch params (`lt`, `sid`, `sk`) issued by the bot
 * server; otherwise the game stays local-only. Silent by design.
 */
import { loadSigner } from "./signer-loader.mjs";

const POLL_MS = 500;
const HEX_64 = /^[0-9a-f]{64}$/;

function readLaunch() {
	const params = new URLSearchParams(window.location.search);
	const launchToken = params.get("lt");
	const sessionId = params.get("sid");
	const sessionKeyHex = params.get("sk");
	if (
		!launchToken ||
		!sessionId ||
		!sessionKeyHex ||
		!HEX_64.test(sessionKeyHex)
	) {
		return null;
	}
	const key = new Uint8Array(32);
	for (let i = 0; i < 32; i++) {
		key[i] = Number.parseInt(sessionKeyHex.slice(i * 2, i * 2 + 2), 16);
	}
	return { launchToken, sessionId, key };
}

function currentScore() {
	const score = Number(window.score);
	return Number.isInteger(score) && score > 0 ? score : 0;
}

function gameOver() {
	return (
		document.getElementById("page_wrap")?.classList.contains("in_result") ??
		false
	);
}

async function reportOnce(launch, score, durationSec) {
	const signer = await loadSigner();
	if (!signer?.setSessionKey(launch.key)) {
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
	});
	if (!tag) {
		return;
	}
	await fetch("/api/setScore", {
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
		}),
	});
}

function watch() {
	const launch = readLaunch();
	if (!launch) {
		return;
	}
	let roundStart = null;
	let reported = false;
	setInterval(() => {
		try {
			const score = currentScore();
			if (score > 0 && roundStart === null) {
				roundStart = Date.now();
			}
			if (score === 0) {
				roundStart = null;
			}
			if (!gameOver()) {
				reported = false;
				return;
			}
			if (score > 0 && !reported && roundStart !== null) {
				reported = true;
				const durationSec = Math.max(
					1,
					Math.round((Date.now() - roundStart) / 1000),
				);
				void reportOnce(launch, score, durationSec).catch(() => {});
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
