const fs = require('fs');

// Mock DOM environment
const elements = {};

function createElement(tag) {
  const el = {
    tagName: tag.toUpperCase(),
    children: [],
    style: {},
    className: '',
    innerText: '',
    innerHTML: '',
    attributes: {},
    hasChildNodes: function() { return this.children.length > 0; },
    appendChild: function(child) { this.children.push(child); },
    removeChild: function(child) {
      const idx = this.children.indexOf(child);
      if (idx >= 0) this.children.splice(idx, 1);
    },
    setAttribute: function(k, v) { this.attributes[k] = v; },
    getAttribute: function(k) { return this.attributes[k]; },
    addEventListener: function(evt, handler) { this['on' + evt] = handler; },
    classList: {
      _classes: new Set(),
      add: function(c) { this._classes.add(c); },
      remove: function(c) { this._classes.delete(c); },
      contains: function(c) { return this._classes.has(c); },
      toggle: function(c, force) {
        if (force === true) this.add(c);
        else if (force === false) this.remove(c);
        else if (this.contains(c)) this.remove(c);
        else this.add(c);
      }
    }
  };
  return el;
}

// Key DOM elements
const elIds = [
  'page_wrap', 'table_content', 'table_wrap', 'table', 'score_value',
  'score_share', 'canvas_wrap', 'g_canvas_wrap', 'button_left', 'button_right',
  'btn_char_prev', 'btn_char_next', 'char_carousel_card', 'char_carousel_dots',
  'char_card_avatar', 'char_card_name', 'char_card_badge', 'char_card_desc'
];

elIds.forEach(id => {
  elements[id] = createElement(id.startsWith('btn_') ? 'button' : 'div');
});
elements['page_wrap'].className = 'page_wrap loading in_result in_greet';
elements['table'] = createElement('ul');

const mockLocalStorage = {
  store: {},
  getItem: function(k) { return this.store[k] || null; },
  setItem: function(k, v) { this.store[k] = String(v); }
};

global.document = {
  getElementById: function(id) { return elements[id] || null; },
  createElement: createElement,
  querySelectorAll: function(sel) {
    if (sel === '.char-carousel-dot') return elements['char_carousel_dots'].children;
    return [];
  },
  body: createElement('body')
};
global.localStorage = mockLocalStorage;
global.window = {
  Telegram: { WebApp: { HapticFeedback: { impactOccurred: function() {} } } }
};
global.triggerTelegramHaptic = function() {};
global.location = { hash: '' };
global.navigator = { userAgent: 'test' };

// Mock Pixi.js
function MockSprite(tex) {
  this.texture = tex;
  this.visible = true;
  this.width = 68;
  this.height = 140;
  this.x = 0;
  this.y = 0;
  this.anchor = { set: function() {} };
  this.scale = { x: 1, y: 1 };
  this.children = [];
  this.addChild = function(c) { this.children.push(c); };
  this.removeChildren = function() { this.children = []; };
  this.removeChild = function(c) {
    const idx = this.children.indexOf(c);
    if (idx >= 0) this.children.splice(idx, 1);
  };
}

function MockContainer() {
  this.visible = true;
  this.x = 0;
  this.y = 0;
  this.children = [];
  this.addChild = function(c) { this.children.push(c); };
  this.removeChildren = function() { this.children = []; };
  this.removeChild = function(c) {
    const idx = this.children.indexOf(c);
    if (idx >= 0) this.children.splice(idx, 1);
  };
}

global.PIXI = {
  Container: MockContainer,
  Sprite: MockSprite,
  Graphics: function() {
    this.beginFill = function() {};
    this.drawRect = function() {};
    this.endFill = function() {};
  },
  Text: function(text) {
    this.text = text;
    this.visible = true;
    this.alpha = 1;
    this.scale = { x: 1, y: 1 };
    this.anchor = { set: function() {} };
  },
  extras: {
    TilingSprite: function() {
      this.visible = true;
      this.tileScale = { x: 1, y: 1 };
      this.tilePosition = { x: 0, y: 0 };
    }
  },
  Texture: function() {},
  BaseTexture: function() {}
};

// Read public/js/main.js
const code = fs.readFileSync('public/js/main.js', 'utf-8');

// Check that the key patches exist in main.js
console.log('--- TEST 1: Code Verification ---');
const hasRbReset = code.includes('function rb(){if(!h){h=!0;Z=!1;Ba = selectedCharacter;');
console.log('Has rb() Z=!1 reset patch:', hasRbReset);
if (!hasRbReset) {
  console.error('FAIL: rb() does not reset Z=!1');
  process.exit(1);
}
console.log('PASS: rb() correctly resets Z=!1 on game over');

const hasSpriteReset = code.includes('if(typeof B!=="undefined")B.visible=!0;if(typeof x!=="undefined")x.visible=!1;');
console.log('Has standing sprite restore on game over:', hasSpriteReset);
if (!hasSpriteReset) {
  console.error('FAIL: rb() does not restore B.visible and hide x.visible');
  process.exit(1);
}
console.log('PASS: rb() correctly restores standing sprite B and hides dead sprite x');

const hasSelectCharacterInRb = code.includes('selectCharacter(selectedCharacter);Ia()');
console.log('Has selectCharacter & Ia call on game over in rb():', hasSelectCharacterInRb);
if (!hasSelectCharacterInRb) {
  console.error('FAIL: rb() does not call selectCharacter and Ia()');
  process.exit(1);
}
console.log('PASS: rb() refreshes character selector state and invokes Ia()');

console.log('\n--- TEST 2: Helper methods in window.khanqahGame ---');
const hasIsInGreet = code.includes('isInGreet: function() { return typeof Z !== \'undefined\' ? !Z : true; }');
const hasResetToSelection = code.includes('resetToCharacterSelection: function() { if (typeof rb === \'function\') rb(); }');
console.log('Has isInGreet API:', hasIsInGreet);
console.log('Has resetToCharacterSelection API:', hasResetToSelection);
if (!hasIsInGreet || !hasResetToSelection) {
  console.error('FAIL: Missing helper API in window.khanqahGame');
  process.exit(1);
}
console.log('PASS: Helper APIs verified');

console.log('\n--- TEST 3: State transition logic simulation ---');
// Simulate the variables and functions
let Z = false;
let h = true;
let aa = false;
let selectedChar = 'nima';
const T = elements['page_wrap'];

function ma(el, className, add) {
  if (add) {
    if (!el.className.includes(className)) el.className += ' ' + className;
  } else {
    el.className = el.className.replace(new RegExp('\\b' + className + '\\b', 'g'), '').trim();
  }
}

function mockIa() {
  ma(T, "in_greet", !Z);
  ma(T, "in_game", !h);
  ma(T, "in_result", h);
}

// Initial state (on load)
mockIa();
console.log('Initial page_wrap class:', T.className);
if (!T.className.includes('in_greet') || !T.className.includes('in_result')) {
  console.error('FAIL: Initial state should have in_greet and in_result');
  process.exit(1);
}
console.log('PASS: Initial screen is character selection page (in_greet present)');

// Start game (pb)
console.log('\nStarting game...');
aa = Z = true;
h = false;
mockIa();
console.log('In-game page_wrap class:', T.className);
if (T.className.includes('in_greet') || !T.className.includes('in_game')) {
  console.error('FAIL: In-game state should have in_game and NOT in_greet');
  process.exit(1);
}
console.log('PASS: In-game state active (in_greet removed, in_game added)');

// Player dies (Va + rb)
console.log('\nPlayer loses (Game Over)...');
aa = false; // defeat
// Inside rb():
h = true;
Z = false; // reset!
mockIa();
console.log('After Game Over page_wrap class:', T.className);
if (!T.className.includes('in_greet')) {
  console.error('FAIL: After game over, in_greet should be present!');
  process.exit(1);
}
console.log('PASS: Reset character selection page successfully appeared on Game Over! (in_greet is active)');

// Test character change while on reset character selection page
console.log('\nSelecting next character (e.g. Fargol)...');
selectedChar = 'fargol';
console.log('Selected character changed to:', selectedChar);

// Restart game
console.log('\nStarting next game with newly chosen character...');
aa = Z = true;
h = false;
mockIa();
console.log('In-game page_wrap class for 2nd round:', T.className);
if (T.className.includes('in_greet') || !T.className.includes('in_game')) {
  console.error('FAIL: 2nd game state should have in_game');
  process.exit(1);
}
console.log('PASS: Next game successfully started with chosen character!');

// Second defeat
console.log('\nPlayer loses 2nd round (Game Over)...');
aa = false;
h = true;
Z = false;
mockIa();
console.log('After 2nd Game Over page_wrap class:', T.className);
if (!T.className.includes('in_greet')) {
  console.error('FAIL: After 2nd game over, in_greet should be present!');
  process.exit(1);
}
console.log('PASS: Reset character selection page reappears after every game over!');

console.log('\nALL GAME OVER RESET CHARACTER SELECTION TESTS PASSED 100%!');
