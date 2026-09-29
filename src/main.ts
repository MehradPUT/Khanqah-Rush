import { Game } from "./engine/Game.ts";
import { TmaBridge } from "./telegram/tma.ts";
import { loadSigner } from "./wasm/signer.ts";
import "./styles/game.css";

window.addEventListener("DOMContentLoaded", () => {
	// Initialize Telegram Mini App Bridge
	const tma = TmaBridge.getInstance();
	console.log(`[Khanqah Rush] Initialized for player: ${tma.getPlayerName()}`);

	const canvas = document.getElementById("gameCanvas") as HTMLCanvasElement;
	if (!canvas) {
		console.error("Canvas element #gameCanvas not found");
		return;
	}

	const game = new Game(canvas);
	game.startLoop();

	// Optional until the signed-score task lands: prove the WASM wiring.
	void loadSigner().then((signer) => {
		console.log(
			`[Khanqah Rush] Signer WASM: ${signer ? `v${signer.version()}` : "unavailable (stub phase)"}`,
		);
	});

	// Export to window for debugging if needed
	(window as unknown as { khanqahGame: Game }).khanqahGame = game;
});
