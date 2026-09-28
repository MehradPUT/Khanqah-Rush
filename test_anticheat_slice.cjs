const fs = require('fs');

const mainJs = fs.readFileSync('public/js/main.js', 'utf8');

// Global mock environment
let ca = 0;
let Fa = () => {};
let R = "eyJuIjoiTmltYSBLIiwiY2kiOi0xMDAxMjM0NTY3ODl9MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=";
let Ba = "نیما";
let lastAlert = null;
let lastSendData = null;
let lastFetch = null;

global.window = {
  Telegram: {
    WebApp: {
      initDataUnsafe: {
        user: { first_name: "نیما", username: "nimak" },
        chat: { id: -100123456789 }
      },
      sendData: (data) => { lastSendData = data; }
    }
  },
  KHANQAH_CONFIG: {
    botToken: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    chatId: -100123456789,
    reportUrl: "/api/testScore"
  }
};
global.fetch = async (url, opts) => {
  lastFetch = { url, body: JSON.parse(opts.body) };
  return { ok: true, json: async () => ({ ok: true }) };
};

// Extract the anti-cheat engine code slice from main.js
const startMarker = '// ==========================================\n// ANTI-CHEAT HONEYPOT SENSORS & CONSOLE BAIT';
const endMarker = 'window.KhanqahAntiCheat = {';
const startIdx = mainJs.indexOf(startMarker);
const endIdx = mainJs.indexOf('};', mainJs.indexOf(endMarker)) + 2;

if (startIdx === -1 || endIdx === -1) {
  console.error("FAIL: Could not locate anti-cheat code slice in public/js/main.js!");
  process.exit(1);
}

const anticheatSlice = mainJs.slice(startIdx, endIdx);
console.log(`Found anti-cheat code slice (${anticheatSlice.length} bytes). Evaluating...`);
eval(anticheatSlice);

console.log("\n--- TEST 1: Initial State & APIs ---");
console.log("window.score initial:", window.score);
console.log("window.setScore exists:", typeof window.setScore === 'function');
console.log("window.Lumberjack.setScore exists:", typeof window.Lumberjack.setScore === 'function');
console.log("window.KhanqahAntiCheat exists:", typeof window.KhanqahAntiCheat === 'object');
console.log("Initial isCheater:", window.KhanqahAntiCheat.isCheater());

if (window.KhanqahAntiCheat.isCheater() !== false) {
  console.error("FAIL: Initially flagged as cheater!");
  process.exit(1);
}
console.log("PASS: Initial state is clean.");

console.log("\n--- TEST 2: Cheater types score = 100 in Console ---");
window.score = 100;
console.log("window.score after assignment:", window.score);
console.log("isCheater flag:", window.KhanqahAntiCheat.isCheater());
console.log("Cheater reason:", window.KhanqahAntiCheat.getReason());

if (window.score !== 100 || !window.KhanqahAntiCheat.isCheater() || window.KhanqahAntiCheat.getReason() !== "console_score_assignment") {
  console.error("FAIL: Console assignment score = 100 did not trigger trap!");
  process.exit(1);
}
console.log("PASS: Console assignment score = 100 successfully triggered the honeypot!");

console.log("\n--- TEST 3: Cheater calls window.setScore({ score: 100 }) ---");
window.setScore({ score: 100 });
console.log("window.score after setScore({ score: 100 }):", window.score);
console.log("isCheater flag:", window.KhanqahAntiCheat.isCheater());
console.log("Cheater reason:", window.KhanqahAntiCheat.getReason());

if (window.score !== 100 || !window.KhanqahAntiCheat.isCheater() || window.KhanqahAntiCheat.getReason() !== "window_setScore") {
  console.error("FAIL: Object setScore({ score: 100 }) did not trigger trap!");
  process.exit(1);
}
console.log("PASS: Object setScore({ score: 100 }) successfully handled and trapped!");

console.log("\n--- TEST 4: Dispatch Telegram Cheater Alert ---");
const playerName = getPlayerDisplayName();
const calloutText = '"' + playerName + '" یه متقلبه!';
console.log("Player name:", playerName);
console.log("Callout text:", calloutText);

dispatchTelegramCheaterAlert(calloutText, playerName, 100);

console.log("Telegram sendData captured:", lastSendData);
console.log("Telegram Bot API fetch captured:", lastFetch);

if (!lastSendData || !lastSendData.includes('یه متقلبه!')) {
  console.error("FAIL: Telegram sendData missing or invalid!");
  process.exit(1);
}

if (!lastFetch || lastFetch.body.text !== '"نیما" یه متقلبه!') {
  console.error("FAIL: Telegram Bot API message text incorrect! Got:", lastFetch ? lastFetch.body.text : null);
  process.exit(1);
}
console.log("PASS: Telegram Bot API dispatched exact message: " + lastFetch.body.text);

console.log("\n--- TEST 5: Legitimate player test (Fallback to کاربر) ---");
Ba = ""; // Clear Ba to test fallback
global.window.Telegram.WebApp.initDataUnsafe.user = null;
const fallbackName = getPlayerDisplayName();
console.log("Fallback player name:", fallbackName);
if (fallbackName !== "کاربر") {
  console.error("FAIL: Expected fallback to 'کاربر', got:", fallbackName);
  process.exit(1);
}
const fallbackText = '"' + fallbackName + '" یه متقلبه!';
console.log("Fallback callout text:", fallbackText);
if (fallbackText !== '"کاربر" یه متقلبه!') {
  console.error("FAIL: Fallback message format mismatch!");
  process.exit(1);
}
console.log("PASS: Fallback message is exact: " + fallbackText);

console.log("\n✅ ALL 5 ANTI-CHEAT HONEYPOT TESTS PASSED 100%!");
