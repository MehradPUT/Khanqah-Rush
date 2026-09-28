# apply_parsa_3s_sleep.py
# Implements: 3 seconds sleep duration, and stops fatigue bar after wake up until user starts chopping.

with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Parsa state variables
old_vars = """// Parsa state (Cozy Blanket Nap on tiredness exhaustion - 2 times max)
var parsaSleepCount = 0;
var parsaSleeping = false;
var parsaSleepTimer = null;"""

new_vars = """// Parsa state (Cozy Blanket Nap on tiredness exhaustion - 2 times max)
var parsaSleepCount = 0;
var parsaSleeping = false;
var parsaWaitingForChop = false;
var parsaSleepStartTime = 0;
var parsaSleepTimer = null;"""

assert old_vars in code, "old_vars not found"
code = code.replace(old_vars, new_vars)

# 2. Add .char-ability-bar-wrap.parsa.waiting CSS
old_css = """    .char-ability-bar-wrap.parsa.sleep {
      background: rgba(45, 20, 60, 0.92);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(241, 196, 15, 0.8);
      box-shadow: 0 0 18px rgba(155, 89, 182, 0.8), 0 0 8px rgba(241, 196, 15, 0.5);
    }"""

new_css = """    .char-ability-bar-wrap.parsa.sleep {
      background: rgba(45, 20, 60, 0.92);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(241, 196, 15, 0.8);
      box-shadow: 0 0 18px rgba(155, 89, 182, 0.8), 0 0 8px rgba(241, 196, 15, 0.5);
    }

    .char-ability-bar-wrap.parsa.waiting {
      background: rgba(18, 38, 26, 0.9);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(46, 204, 113, 0.8);
      box-shadow: 0 0 14px rgba(46, 204, 113, 0.4);
    }

    .char-ability-bar-wrap.parsa.waiting .char-hud-title {
      color: #2ecc71;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.parsa.waiting .char-hud-timer {
      color: #2ecc71;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.parsa.waiting .char-hud-fill {
      background: #2ecc71;
      box-shadow: 0 0 8px rgba(46, 204, 113, 0.8);
    }"""

assert old_css in code, "old_css not found"
code = code.replace(old_css, new_css)

# 3. Update triggerParsaNap
old_trigger = """function triggerParsaNap() {
  if (typeof aa === 'undefined' || !aa) return;
  if (parsaSleeping) return;
  parsaSleeping = true;
  parsaSleepCount++;
  ba = +new Date + qa; // Full stamina restored!

  spawnCombatPopup('🛌 خواب و پتو! تجدید قوا (' + parsaSleepCount + '/2) 💤', 'crit');
  triggerTelegramHaptic('heavy');

  if (typeof sa !== 'undefined' && tex_parsa_sleep) {
    sa.texture = tex_parsa_sleep;
    sa.width = 68;
    sa.height = 140;
  }
  if (typeof ta !== 'undefined' && tex_parsa_sleep) {
    ta.texture = tex_parsa_sleep;
    ta.width = 68;
    ta.height = 140;
  }

  var remB = Math.max(0, 2 - parsaSleepCount);
  var pct = (remB / 2) * 100;
  updateCharacterHUD('parsa', 'sleep', pct, remB + '/2 پتو', false);

  if (parsaSleepTimer) clearTimeout(parsaSleepTimer);
  parsaSleepTimer = setTimeout(function() {
    parsaSleeping = false;
    if (typeof sa !== 'undefined' && aa && tex_parsa_body) {
      sa.texture = tex_parsa_body;
      sa.width = 68;
      sa.height = 140;
    }
    if (typeof ta !== 'undefined' && tex_parsa_body) {
      ta.texture = tex_parsa_body;
      ta.width = 68;
      ta.height = 140;
    }
    updateCharacterHUD('parsa', 'normal', pct, remB + '/2 پتو', false);
  }, 1200);
}"""

new_trigger = """function triggerParsaNap() {
  if (typeof aa === 'undefined' || !aa) return;
  if (parsaSleeping) return;
  parsaSleeping = true;
  parsaWaitingForChop = false;
  parsaSleepCount++;
  parsaSleepStartTime = +new Date;
  za = false; // Stop game fatigue timer immediately!
  ba = +new Date + qa; // Full stamina restored!
  if (typeof Ua === 'function') Ua(); // Lock fatigue bar at 100% full

  spawnCombatPopup('🛌 خواب ۳ ثانیه‌ای! تجدید قوا (' + parsaSleepCount + '/2) 💤', 'crit');
  triggerTelegramHaptic('heavy');

  if (typeof sa !== 'undefined' && tex_parsa_sleep) {
    sa.texture = tex_parsa_sleep;
    sa.width = 68;
    sa.height = 140;
  }
  if (typeof ta !== 'undefined' && tex_parsa_sleep) {
    ta.texture = tex_parsa_sleep;
    ta.width = 68;
    ta.height = 140;
  }

  var remB = Math.max(0, 2 - parsaSleepCount);
  updateCharacterHUD('parsa', 'sleep', 100, '3.0s خواب', false);

  if (parsaSleepTimer) clearTimeout(parsaSleepTimer);
  parsaSleepTimer = setTimeout(function() {
    // WAKE UP AFTER 3 SECONDS!
    parsaSleeping = false;
    parsaWaitingForChop = true; // Stop fatigue bar until user starts chopping!
    za = false; // Keep fatigue bar stopped!
    ba = +new Date + qa;
    if (typeof Ua === 'function') Ua();

    if (typeof sa !== 'undefined' && aa && tex_parsa_body) {
      sa.texture = tex_parsa_body;
      sa.width = 68;
      sa.height = 140;
    }
    if (typeof ta !== 'undefined' && tex_parsa_body) {
      ta.texture = tex_parsa_body;
      ta.width = 68;
      ta.height = 140;
    }

    spawnCombatPopup('⏰ بیدار شد! آماده برای تبر زدن! 🪓', 'young');
    triggerTelegramHaptic('medium');
    updateCharacterHUD('parsa', 'waiting', 100, 'آماده تبر (' + remB + '/2)', false);
  }, 3000);
}"""

assert old_trigger in code, "old_trigger not found"
code = code.replace(old_trigger, new_trigger)

# 4. In updateCharacterHUD, handle phase === 'waiting'
old_hud_titles = """    if (nameEl) {
      nameEl.innerText = (phase === 'sleep' ? '💤 parsa (خواب)' : '🛌 parsa');
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'sleep' ? '🛌 خواب و پتو!' : 'تجدید قوا با پتو');
    }"""

new_hud_titles = """    if (nameEl) {
      nameEl.innerText = (phase === 'sleep' ? '💤 parsa (خواب ۳s)' : (phase === 'waiting' ? '🪓 parsa (بیدار)' : '🛌 parsa'));
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'sleep' ? '🛌 خواب ۳ ثانیه‌ای!' : (phase === 'waiting' ? 'تایمر متوقف! تبر بزن' : 'تجدید قوا با پتو'));
    }"""

assert old_hud_titles in code, "old_hud_titles not found"
code = code.replace(old_hud_titles, new_hud_titles)

# 5. In window.khanqahGame
old_kg = """  getParsaSleepCount: function() { return parsaSleepCount; },
  isParsaSleeping: function() { return parsaSleeping; },"""

new_kg = """  getParsaSleepCount: function() { return parsaSleepCount; },
  isParsaSleeping: function() { return parsaSleeping; },
  isParsaWaitingForChop: function() { return parsaWaitingForChop; },"""

assert old_kg in code, "old_kg not found"
code = code.replace(old_kg, new_kg)

# 6. In pb() reset
old_pb = """  parsaSleepCount = 0;
  parsaSleeping = false;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }"""

new_pb = """  parsaSleepCount = 0;
  parsaSleeping = false;
  parsaWaitingForChop = false;
  parsaSleepStartTime = 0;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }"""

assert old_pb in code, "old_pb not found"
code = code.replace(old_pb, new_pb)

# 7. In Ta() (allow execution when parsaSleeping or parsaWaitingForChop)
old_ta_head = "  if (aa && za) {"
new_ta_head = "  if (aa && (za || (selectedCharacter === 'parsa' && (parsaSleeping || parsaWaitingForChop)))) {"

assert old_ta_head in code, "old_ta_head not found"
code = code.replace(old_ta_head, new_ta_head)

# In Ta() parsa branch:
old_ta_parsa = """    } else if (selectedCharacter === 'parsa') {
      var remB = Math.max(0, 2 - parsaSleepCount);
      if (parsaSleeping) {
        ba = +new Date + qa; // Stamina held at max during nap
        updateCharacterHUD('parsa', 'sleep', (remB / 2) * 100, remB + '/2 پتو', false);
      } else {
        updateCharacterHUD('parsa', 'normal', (remB / 2) * 100, remB + '/2 پتو', false);
      }"""

new_ta_parsa = """    } else if (selectedCharacter === 'parsa') {
      var remB = Math.max(0, 2 - parsaSleepCount);
      if (parsaSleeping) {
        var sleepElapsed = +new Date - parsaSleepStartTime;
        var remSleep = Math.max(0, (3000 - sleepElapsed) / 1000).toFixed(1);
        ba = +new Date + qa; // Stamina held full
        if (typeof Ua === 'function') Ua(); // Keep fatigue bar full
        updateCharacterHUD('parsa', 'sleep', Math.max(0, ((3000 - sleepElapsed) / 3000) * 100), remSleep + 's خواب', false);
      } else if (parsaWaitingForChop) {
        ba = +new Date + qa; // Fatigue bar stopped until user starts chopping!
        if (typeof Ua === 'function') Ua(); // Keep fatigue bar full at 100%
        updateCharacterHUD('parsa', 'waiting', 100, 'آماده تبر (' + remB + '/2)', false);
      } else {
        updateCharacterHUD('parsa', 'normal', (remB / 2) * 100, remB + '/2 پتو', false);
      }"""

assert old_ta_parsa in code, "old_ta_parsa not found"
code = code.replace(old_ta_parsa, new_ta_parsa)

# 8. In Ca(a) (ignore chops during 3s sleep, resume fatigue bar on wake chop)
old_ca_parsa = """  if (aa && selectedCharacter === 'parsa' && parsaSleeping) {
    parsaSleeping = false;
    if (parsaSleepTimer) {
      clearTimeout(parsaSleepTimer);
      parsaSleepTimer = null;
    }
    if (typeof sa !== 'undefined' && tex_parsa_body) {
      sa.texture = tex_parsa_body;
      sa.width = 68;
      sa.height = 140;
    }
  }"""

new_ca_parsa = """  if (aa && selectedCharacter === 'parsa') {
    if (parsaSleeping) {
      // Still asleep during 3 seconds: ignore chop inputs!
      return;
    }
    if (parsaWaitingForChop) {
      parsaWaitingForChop = false;
      za = true; // User started chopping, resume fatigue bar!
      ba = +new Date + qa;
    }
  }"""

assert old_ca_parsa in code, "old_ca_parsa not found"
code = code.replace(old_ca_parsa, new_ca_parsa)

# 9. In Va() (reset parsaWaitingForChop on defeat)
old_va = """  aliFlurryActive = false;
  aliFlurryRemaining = 0;
  parsaSleeping = false;"""

new_va = """  aliFlurryActive = false;
  aliFlurryRemaining = 0;
  parsaSleeping = false;
  parsaWaitingForChop = false;"""

assert old_va in code, "old_va not found"
code = code.replace(old_va, new_va)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("scratch/patch_lumberjack.py updated successfully with 3-second sleep and fatigue pause until chop!")
