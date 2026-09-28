const fs = require('fs');

// Test credentials come from env; fall back to dummy fixtures so tests run offline.
// Copy .env.example to .env and set real values for live bot testing.
// Never commit real tokens - see .gitignore.
const TEST_CHAT_ID = Number(process.env.TELEGRAM_CHAT_ID) || -100123456789;

const elements = {};
function createElement(tag) {
  return {
    tagName: tag.toUpperCase(),
    children: [],
    style: {},
    className: '',
    innerText: '',
    innerHTML: '',
    attributes: {},
    appendChild: function(c) { this.children.push(c); },
    addEventListener: function(evt, handler) { this['on' + evt] = handler; },
    classList: { add: () => {}, remove: () => {} }
  };
}

['page_wrap', 'score_value', 'table_wrap', 'table', 'score_share', 'table_content',
 'canvas_wrap', 'g_canvas_wrap', 'button_left', 'button_right',
 'btn_char_prev', 'btn_char_next', 'char_carousel_card', 'char_carousel_dots',
 'char_card_avatar', 'char_card_name', 'char_card_badge', 'char_card_desc'].forEach(id => {
  elements[id] = createElement('div');
});

global.document = {
  getElementById: (id) => elements[id] || null,
  createElement: createElement,
  querySelectorAll: () => [],
  body: createElement('body')
};

global.Image = function() {
  var img = {
    src: '',
    width: 100,
    height: 100,
    onload: null,
    onerror: null
  };
  setTimeout(() => { if (img.onload) img.onload(); }, 10);
  return img;
};

global.localStorage = {
  store: {},
  getItem: (k) => global.localStorage.store[k] || null,
  setItem: (k, v) => { global.localStorage.store[k] = String(v); }
};

global.window = global;
global.window.document = global.document;
global.window.localStorage = global.localStorage;
global.window.location = { hash: "#eyJuIjoiTmltYSBLIiwiY2kiOi0xMDAxMjM0NTY3ODl9MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=" };
global.window.devicePixelRatio = 2;

global.Telegram = {
  WebApp: {
    ready: () => {},
    expand: () => {},
    enableClosingConfirmation: () => {},
    initDataUnsafe: {
      user: { first_name: "نیما", username: "nimak" },
      chat: { id: TEST_CHAT_ID }
    },
    sendData: (data) => {
      global.window.__lastSendData = data;
    }
  }
};

let lastXhrPayload = null;
global.XMLHttpRequest = function() {
  this.open = (method, url) => { this.url = url; };
  this.send = (data) => {
    lastXhrPayload = new URLSearchParams(data);
    this.readyState = 4;
    this.status = 200;
    this.responseText = JSON.stringify({ scores: [{ pos: 1, score: 250, name: "نیما", current: true }], "new": true });
    if (this.onreadystatechange) this.onreadystatechange();
  };
};

global.fetch = async (url, opts) => {
  global.window.__lastFetch = { url, body: JSON.parse(opts.body) };
  return { ok: true, json: async () => ({ ok: true }) };
};

const code = fs.readFileSync('public/js/main.js', 'utf8');

console.log("Evaluating public/js/main.js...");
try {
  eval(code);
  console.log("✓ main.js evaluated cleanly without errors!");
} catch (e) {
  console.error("Eval error:", e);
  process.exit(1);
}

// TEST 1: Check AntiCheat API and Console Bait existence
console.log("\n--- TEST 1: Checking Console Bait & Decoy APIs ---");
console.log("window.score initial:", window.score);
console.log("window.setScore exists:", typeof window.setScore === 'function');
console.log("window.Lumberjack.setScore exists:", typeof window.Lumberjack.setScore === 'function');
console.log("window.KhanqahAntiCheat exists:", typeof window.KhanqahAntiCheat === 'object');
console.log("Initial isCheater:", window.KhanqahAntiCheat.isCheater());

if (typeof window.setScore !== 'function' || !window.KhanqahAntiCheat) {
  console.error("FAIL: Anti-cheat functions missing!");
  process.exit(1);
}

// TEST 2: Cheater enters score = 100 via console
console.log("\n--- TEST 2: Cheater types score = 100 in console ---");
window.score = 100;
console.log("window.score after assignment:", window.score);
console.log("DOM score_value display:", elements['score_value'].innerHTML);
console.log("isCheater flag:", window.KhanqahAntiCheat.isCheater());
console.log("Cheater reason:", window.KhanqahAntiCheat.getReason());

if (window.score !== 100 || !window.KhanqahAntiCheat.isCheater()) {
  console.error("FAIL: Console score assignment not caught!");
  process.exit(1);
}

// TEST 3: Cheater uses setScore({ score: 250 })
console.log("\n--- TEST 3: Cheater calls setScore({ score: 250 }) ---");
window.setScore({ score: 250 });
console.log("window.score after object assignment:", window.score);
console.log("DOM score_value display:", elements['score_value'].innerHTML);
console.log("isCheater flag:", window.KhanqahAntiCheat.isCheater());

if (window.score !== 250 || !window.KhanqahAntiCheat.isCheater()) {
  console.error("FAIL: Object score assignment not caught!");
  process.exit(1);
}

// TEST 4: Verification of the Telegram Alert Message
console.log("\n--- TEST 4: Telegram Callout Message & Payload Format ---");
window.khanqahGame.kill();

setTimeout(() => {
  console.log("Payload 'cheater':", lastXhrPayload ? lastXhrPayload.get('cheater') : 'null');
  console.log("Payload 'score':", lastXhrPayload ? lastXhrPayload.get('score') : 'null');
  console.log("Payload 'token':", lastXhrPayload ? lastXhrPayload.get('token') : 'null');
  console.log("Payload 'message':", lastXhrPayload ? lastXhrPayload.get('message') : 'null');
  console.log("Telegram sendData sent:", global.window.__lastSendData);

  if (!lastXhrPayload || lastXhrPayload.get('cheater') !== '1') {
    console.error("FAIL: Cheater payload not flagged!");
    process.exit(1);
  }

  const callout = lastXhrPayload.get('message');
  if (!callout.includes('یه متقلبه!')) {
    console.error("FAIL: Callout text does not contain 'یه متقلبه!'");
    process.exit(1);
  }

  console.log("\n✅ ALL ANTI-CHEAT HONEYPOT TESTS PASSED 100%!");
  process.exit(0);
}, 500);
