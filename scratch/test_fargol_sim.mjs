import fs from 'fs';
import { JSDOM } from 'jsdom';
import * as PIXI from 'pixi.js-legacy';

const dom = new JSDOM(`<!DOCTYPE html><html><body><div id="game-container"></div></body></html>`, {
  url: "http://localhost",
  pretendToBeVisual: true
});
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.PIXI = PIXI;
global.selectedCharacter = 'fargol';
global.characterVolumes = {};

// Mocks
global.initCharacterSelector = () => {};
global.spawnCombatPopup = (msg, type) => console.log('POPUP:', msg);
global.updateCharacterHUD = (c, s, p, t, a) => console.log('HUD:', c, s, p, t, 'ability:', a);
global.triggerTelegramHaptic = () => {};
global.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });

const code = fs.readFileSync('public/js/main.js', 'utf8');
try {
  eval(code);
  console.log("Syntax is valid.");
  console.log("sa.width:", sa.width, "sa.height:", sa.height);
  if (typeof K !== 'undefined') console.log("Game loaded!");
  
  // Trigger a chop
  aa = true; // prevent early death
  mb(true); // Call chop
  console.log("mb() called. sa texture:", sa.texture ? 'present' : 'null');
  
} catch (e) {
  console.error("Eval error:", e);
}
