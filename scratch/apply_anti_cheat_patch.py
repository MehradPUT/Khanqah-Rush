import re

with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    patch = f.read()

# 1. Anti-Cheat Engine & Honeypot Trap code to insert after window.khanqahGame
anticheat_engine_code = '''
// ==========================================
// ANTI-CHEAT HONEYPOT SENSORS & CONSOLE BAIT
// ==========================================
var _honeypot_cheated = false;
var _honeypot_reason = "";
var _shadow_score = 0 ^ 0x5F3759DF;
var _chop_count = 0;
var _game_start_time = 0;
var _recent_chops = [];

function _syncShadowScore() {
  _shadow_score = ca ^ 0x5F3759DF;
}

function _onCheatScoreInput(val, source) {
  var num = 0;
  if (typeof val === 'object' && val !== null) {
    num = val.score !== undefined ? val.score : (val.s !== undefined ? val.s : 0);
  } else {
    num = parseInt(val, 10);
  }
  if (isNaN(num)) num = 0;
  
  ca = num;
  _syncShadowScore();
  _honeypot_cheated = true;
  _honeypot_reason = source || "console_score_tampering";
  
  // Immediately update UI score so cheater sees their entered score on screen:
  Fa();
  
  try {
    console.log("%c✓ Score set to " + num + " (Honeypot Active)", "color: #2e7d32; font-weight: bold; font-size: 13px;");
    console.log("%cGame status: Score updated successfully.", "color: #555;");
  } catch(e) {}
  
  return { success: true, score: ca };
}

try {
  Object.defineProperty(window, "score", {
    get: function() { return ca; },
    set: function(val) { _onCheatScoreInput(val, "console_score_assignment"); },
    configurable: true
  });
} catch(e) {}

window.setScore = function(val) { return _onCheatScoreInput(val, "window_setScore"); };

window.game = window.game || {};
try {
  Object.defineProperty(window.game, "score", {
    get: function() { return ca; },
    set: function(val) { _onCheatScoreInput(val, "game_score_assignment"); },
    configurable: true
  });
} catch(e) {}
window.game.setScore = function(val) { return _onCheatScoreInput(val, "game_setScore"); };

window.Lumberjack = window.Lumberjack || {};
window.Lumberjack.setScore = function(val) { return _onCheatScoreInput(val, "lumberjack_setScore"); };
window.Lumberjack.getScore = function() { return ca; };

function getPlayerDisplayName() {
  if (typeof Ba === 'string' && Ba.length > 0) return Ba;
  try {
    var tgUser = window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user;
    if (tgUser) {
      if (tgUser.first_name) return tgUser.first_name;
      if (tgUser.username) return "@" + tgUser.username;
    }
  } catch(e) {}
  return "کاربر";
}

function generateScoreToken(score, startTime, chopCount) {
  var seed = (score * 31 + chopCount * 17 + Math.floor(startTime / 1000)) ^ 0x5A5A5A5A;
  return "OK_" + Math.abs(seed).toString(16);
}

function dispatchTelegramCheaterAlert(calloutText, playerName, score) {
  // 1. If in Telegram Mini App and sendData is available:
  try {
    if (window.Telegram && window.Telegram.WebApp && typeof window.Telegram.WebApp.sendData === 'function') {
      window.Telegram.WebApp.sendData(JSON.stringify({
        type: "cheater_alert",
        user: playerName,
        text: calloutText,
        score: score
      }));
    }
  } catch(e) {}

  // 2. Direct Telegram Bot API if configured:
  try {
    var cfg = window.KHANQAH_CONFIG || {};
    var botToken = cfg.botToken || window.TELEGRAM_BOT_TOKEN;
    var chatId = cfg.chatId || window.TELEGRAM_CHAT_ID;

    if (!chatId && R) {
      try {
        var rawR = decodeURIComponent(escape(atob(R)));
        var parsedR = JSON.parse(rawR.substr(0, rawR.length - 32));
        chatId = parsedR.ci || parsedR.chat_id || (parsedR.chat && parsedR.chat.id);
      } catch(e) {}
    }
    if (!chatId && window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.chat) {
      chatId = window.Telegram.WebApp.initDataUnsafe.chat.id;
    }

    if (botToken && chatId) {
      fetch("https://api.telegram.org/bot" + botToken + "/sendMessage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: calloutText
        })
      }).catch(function() {});
    }
  } catch(e) {}

  try {
    console.warn("%c🚨 [HONEYPOT ALERT] Cheater flagged! Telegram Message: " + calloutText, "color: #d32f2f; font-weight: bold; font-size: 14px;");
  } catch(e) {}
}

window.KhanqahAntiCheat = {
  isCheater: function() { return _honeypot_cheated; },
  getReason: function() { return _honeypot_reason; },
  getShadowScore: function() { return _shadow_score; },
  triggerTrap: function(reason) { _honeypot_cheated = true; _honeypot_reason = reason || 'manual_test'; }
};
'''

# Insert anticheat_engine_code right after window.khanqahGame = { ... };
target_end = 'window.khanqahGame = {\n'
assert target_end in patch, "target_end not found"

# Find the closing brace of window.khanqahGame
pos = patch.find(target_end)
pos_close = patch.find('};\n// ----------------------------------------------------', pos)
assert pos_close != -1, "pos_close not found"

insert_pos = pos_close + 2  # after '};'
patch = patch[:insert_pos] + '\n' + anticheat_engine_code + patch[insert_pos:]

# 2. Update Ca(a) -> Ca(a, e) with untrusted event & CPS check
ca_pattern_old = "ca_pattern = r'function Ca\(a\)\s*\{'"
ca_pattern_new = "code = re.sub(r'function Ca\(a\)\s*\{', 'function Ca(a, e) {', code, count=1)\nca_pattern = r'function Ca\(a, e\)\s*\{'"
patch = patch.replace(ca_pattern_old, ca_pattern_new)

# Add anti-cheat check at the beginning of ca_pre_injection
old_pre = "ca_pre_injection = '''"
new_pre = "ca_pre_injection = '''\n  if (e && e.isTrusted === false) {\n    _honeypot_cheated = true;\n    _honeypot_reason = 'untrusted_event';\n  }\n  var _nowChop = +new Date;\n  if (!_game_start_time) _game_start_time = _nowChop;\n  _chop_count++;\n  _recent_chops.push(_nowChop);\n  while (_recent_chops.length > 0 && _recent_chops[0] < _nowChop - 1000) {\n    _recent_chops.shift();\n  }\n  var _elapsedSec = (_nowChop - _game_start_time) / 1000;\n  if (_recent_chops.length > 14 || (_elapsedSec > 1.5 && (_chop_count / _elapsedSec) > 14)) {\n    _honeypot_cheated = true;\n    _honeypot_reason = 'inhuman_cps';\n  }\n"
patch = patch.replace(old_pre, new_pre, 1)

# Add _syncShadowScore() on Fargol & Ahmad early exits
patch = patch.replace("ba = +new Date + qa;\n      ca++;\n      ca % 20", "ba = +new Date + qa;\n      ca++;\n      _syncShadowScore();\n      ca % 20")

# Add _syncShadowScore() before wa(a,!0,2==Math.abs(b)) in chop
patch = patch.replace("wa(a,!0,2==Math.abs(b))'''\n)", "_syncShadowScore();\n    wa(a,!0,2==Math.abs(b))'''\n)")

# 3. Add reset in pb()
reset_hook = """
# Anti-cheat state reset on new game:
code = code.replace(
    'ca=0;Ha=1;ra=za=!1;',
    'ca=0;_honeypot_cheated=!1;_honeypot_reason="";_syncShadowScore();_chop_count=0;_game_start_time=+new Date;_recent_chops=[];Ha=1;ra=za=!1;'
)
"""

# 4. Add qb() and rb() and event listeners
network_hooks = """
# Anti-cheat score submission in qb() and game-over check in rb():
old_qb = 'function qb(){R&&gb("/api/setScore",{data:R,score:ca||0},function(a){l=a.scores;bb();ya();a["new"]&&h&&(ra=!0,ma(Ja,"shown",ra))})}'
new_qb = '''function qb() {
  var isCheat = _honeypot_cheated || ((ca ^ 0x5F3759DF) !== _shadow_score);
  var elapsedSec = Math.max(1, Math.round((+new Date - (_game_start_time || +new Date)) / 1000));
  var curCps = Math.round((_chop_count || 1) / elapsedSec);
  if (ca > 40 && elapsedSec < 2.5) {
    isCheat = true;
    _honeypot_reason = _honeypot_reason || "impossible_speed";
  }

  var playerName = getPlayerDisplayName();
  var calloutText = '"' + playerName + '" یه متقلبه!';
  var tokenVal = isCheat ? ("FLAGGED_" + (_honeypot_reason || "honeypot")) : generateScoreToken(ca, _game_start_time, _chop_count);

  var payload = {
    data: R || "",
    score: ca || 0,
    token: tokenVal,
    cheater: isCheat ? 1 : 0,
    reason: isCheat ? _honeypot_reason : "",
    cps: curCps,
    duration: elapsedSec,
    message: calloutText
  };

  if (R || (window.KHANQAH_CONFIG && window.KHANQAH_CONFIG.reportUrl)) {
    var targetUrl = (window.KHANQAH_CONFIG && window.KHANQAH_CONFIG.reportUrl) || "/api/setScore";
    gb(targetUrl, payload, function(a) {
      if (a && a.scores) {
        l = a.scores;
        bb();
        ya();
        a["new"] && h && (ra = !0, ma(Ja, "shown", ra));
      }
    });
  }

  if (isCheat) {
    dispatchTelegramCheaterAlert(calloutText, playerName, ca);
  }
}'''
code = code.replace(old_qb, new_qb)

code = code.replace('ca>cb?qb():hb()', '(_honeypot_cheated||ca>cb)?qb():hb()')

old_listeners = 'N(La,Ma,function(){Z||Da.sound.play("hit1",{volume:0});!Z||h?fb():Ca(!0)});N(jb,\\nMa,function(){aa&&Ca(!1)});'
new_listeners = 'N(La,Ma,function(e){Z||Da.sound.play("hit1",{volume:0});!Z||h?fb():Ca(!0,e)});N(jb,\\nMa,function(e){aa&&Ca(!1,e)});'
code = code.replace(old_listeners, new_listeners)
"""

# Replace old_keydown with the full listener that captures keydown event:
patch = patch.replace(
    "new_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):(37==a?rotateCharacter(-1):(39==a?rotateCharacter(1):(Z&&!h||32!=a||(Ka(La),fb()))))'\ncode = code.replace(old_keydown, new_keydown)",
    "new_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):(37==a?rotateCharacter(-1):(39==a?rotateCharacter(1):(Z&&!h||32!=a||(Ka(La),fb()))))'\ncode = code.replace(old_keydown, new_keydown)\n" + reset_hook + network_hooks
)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(patch)

print("scratch/patch_lumberjack.py updated successfully!")
