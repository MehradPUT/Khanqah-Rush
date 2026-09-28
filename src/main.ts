import { Game } from './engine/Game.ts';
import { TmaBridge } from './telegram/tma.ts';

window.addEventListener('DOMContentLoaded', () => {
  // Initialize Telegram Mini App Bridge
  const tma = TmaBridge.getInstance();
  console.log(`[Khanqah Rush] Initialized for player: ${tma.getPlayerName()}`);

  const canvas = document.getElementById('gameCanvas') as HTMLCanvasElement;
  if (!canvas) {
    console.error('Canvas element #gameCanvas not found');
    return;
  }

  const game = new Game(canvas);
  game.startLoop();

  // Export to window for debugging if needed
  (window as unknown as { khanqahGame: Game }).khanqahGame = game;
});
