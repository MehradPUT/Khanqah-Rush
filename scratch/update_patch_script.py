# Update scratch/patch_lumberjack.py to include Parsa
with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    patch = f.read()

# 1. Update Title and add Parsa state variables
patch = patch.replace(
    "// --- MULTI-CHARACTER (NIMA, FARGOL, ALI & AMIRHOSSEIN) GAME ENGINE ---",
    "// --- MULTI-CHARACTER (NIMA, FARGOL, ALI, AMIRHOSSEIN & PARSA) GAME ENGINE ---"
)

old_vars = """// Texture pointers
var tex_nima_old = null;"""

new_vars = """// Parsa state (Cozy Blanket Nap on tiredness exhaustion - 2 times max)
var parsaSleepCount = 0;
var parsaSleeping = false;
var parsaSleepTimer = null;

// Texture pointers
var tex_nima_old = null;"""

patch = patch.replace(old_vars, new_vars)

old_tex_ptrs = """var tex_amirhossein_died = null;"""
new_tex_ptrs = """var tex_amirhossein_died = null;
var tex_parsa_body = null;
var tex_parsa_swing = null;
var tex_parsa_sleep = null;
var tex_parsa_died = null;"""

patch = patch.replace(old_tex_ptrs, new_tex_ptrs)

# 2. Update .char-select-bar CSS and add Parsa button CSS
old_char_bar_css = """    .char-select-bar {
      display: flex;
      justify-content: center;
      gap: 4px;
      margin: 10px auto 16px auto;
      max-width: 380px;
      padding: 3px 5px;"""

new_char_bar_css = """    .char-select-bar {
      display: flex;
      justify-content: center;
      gap: 3px;
      margin: 10px auto 16px auto;
      max-width: 440px;
      padding: 3px 4px;"""

patch = patch.replace(old_char_bar_css, new_char_bar_css)

old_char_btn_css = """    .char-tab-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      background: transparent;
      border: 1.5px solid transparent;
      padding: 5px 6px;
      border-radius: 14px;
      cursor: pointer;
      color: #c9d1d9;
      transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
      -webkit-tap-highlight-color: transparent;
      outline: none;
    }

    .char-tab-avatar {
      font-size: 20px;
      line-height: 1;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
    }

    .char-tab-text {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      line-height: 1.1;
    }

    .char-tab-name {
      font-family: 'Arial Black', Impact, sans-serif;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: 0.4px;
      color: #ffffff;
      text-transform: lowercase;
    }

    .char-tab-badge {
      font-family: 'Vazirmatn', sans-serif;
      font-size: 10px;
      font-weight: 800;
      color: #e4b072;
    }"""

new_char_btn_css = """    .char-tab-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      background: transparent;
      border: 1.5px solid transparent;
      padding: 4px 4px;
      border-radius: 14px;
      cursor: pointer;
      color: #c9d1d9;
      transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
      -webkit-tap-highlight-color: transparent;
      outline: none;
    }

    .char-tab-avatar {
      font-size: 18px;
      line-height: 1;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
    }

    .char-tab-text {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      line-height: 1.1;
    }

    .char-tab-name {
      font-family: 'Arial Black', Impact, sans-serif;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 0.4px;
      color: #ffffff;
      text-transform: lowercase;
    }

    .char-tab-badge {
      font-family: 'Vazirmatn', sans-serif;
      font-size: 9px;
      font-weight: 800;
      color: #e4b072;
    }"""

patch = patch.replace(old_char_btn_css, new_char_btn_css)

old_amirhossein_btn_css = """    .char-tab-btn.active[data-char="amirhossein"] .char-tab-badge {
      color: #70a1ff;
    }"""

new_parsa_btn_css = """    .char-tab-btn.active[data-char="amirhossein"] .char-tab-badge {
      color: #70a1ff;
    }

    .char-tab-btn.active[data-char="parsa"] {
      background: linear-gradient(135deg, rgba(155, 89, 182, 0.35) 0%, rgba(142, 68, 173, 0.25) 100%);
      border-color: #9b59b6;
      box-shadow: 0 0 14px rgba(155, 89, 182, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.4);
    }

    .char-tab-btn.active[data-char="parsa"] .char-tab-badge {
      color: #d7bde2;
    }"""

patch = patch.replace(old_amirhossein_btn_css, new_parsa_btn_css)

old_amirhossein_bar_css = """    .char-ability-bar-wrap.amirhossein.normal {
      background: rgba(13, 27, 42, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(41, 128, 185, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(41, 128, 185, 0.3);
    }"""

new_parsa_bar_css = """    .char-ability-bar-wrap.amirhossein.normal {
      background: rgba(13, 27, 42, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(41, 128, 185, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(41, 128, 185, 0.3);
    }

    .char-ability-bar-wrap.parsa.normal {
      background: rgba(26, 18, 38, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(155, 89, 182, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(155, 89, 182, 0.3);
    }

    .char-ability-bar-wrap.parsa.sleep {
      background: rgba(45, 20, 60, 0.92);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(241, 196, 15, 0.8);
      box-shadow: 0 0 18px rgba(155, 89, 182, 0.8), 0 0 8px rgba(241, 196, 15, 0.5);
    }"""

patch = patch.replace(old_amirhossein_bar_css, new_parsa_bar_css)

old_amirhossein_title_css = """    .char-ability-bar-wrap.amirhossein.normal .char-hud-title {
      color: #70a1ff;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }"""

new_parsa_title_css = """    .char-ability-bar-wrap.amirhossein.normal .char-hud-title {
      color: #70a1ff;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.parsa.normal .char-hud-title,
    .char-ability-bar-wrap.parsa.sleep .char-hud-title {
      color: #d7bde2;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }"""

patch = patch.replace(old_amirhossein_title_css, new_parsa_title_css)

old_amirhossein_timer_css = """    .char-ability-bar-wrap.amirhossein.normal .char-hud-timer {
      color: #70a1ff;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }"""

new_parsa_timer_css = """    .char-ability-bar-wrap.amirhossein.normal .char-hud-timer {
      color: #70a1ff;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.parsa.normal .char-hud-timer,
    .char-ability-bar-wrap.parsa.sleep .char-hud-timer {
      color: #f5b041;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.parsa .char-hud-fill {
      background: linear-gradient(90deg, #8e44ad 0%, #9b59b6 50%, #f1c40f 100%);
      box-shadow: 0 0 8px rgba(155, 89, 182, 0.7);
    }"""

patch = patch.replace(old_amirhossein_timer_css, new_parsa_timer_css)

# 3. Add triggerParsaNap before updateCharacterHUD
trigger_parsa_nap_fn = """function triggerParsaNap() {
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
}

function updateCharacterHUD"""

patch = patch.replace("function updateCharacterHUD", trigger_parsa_nap_fn)

# 4. In updateCharacterHUD, add charId === 'parsa'
old_hud_amirhossein = """  } else if (charId === 'amirhossein') {
    if (shieldEl) {
      shieldEl.style.display = 'none';
    }
    if (nameEl) {
      nameEl.innerText = '🧢 amirhossein';
    }
    if (titleEl) {
      titleEl.innerText = 'امتیاز ۲ برابر (۲X)';
    }"""

new_hud_parsa = """  } else if (charId === 'amirhossein') {
    if (shieldEl) {
      shieldEl.style.display = 'none';
    }
    if (nameEl) {
      nameEl.innerText = '🧢 amirhossein';
    }
    if (titleEl) {
      titleEl.innerText = 'امتیاز ۲ برابر (۲X)';
    }
  } else if (charId === 'parsa') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      var remB = Math.max(0, 2 - parsaSleepCount);
      shieldEl.innerText = remB > 0 ? '🛌 ' + remB + ' پتو' : '💤 بدون پتو';
      shieldEl.className = 'char-hud-shield ' + (remB > 0 ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = (phase === 'sleep' ? '💤 parsa (خواب)' : '🛌 parsa');
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'sleep' ? '🛌 خواب و پتو!' : 'تجدید قوا با پتو');
    }"""

patch = patch.replace(old_hud_amirhossein, new_hud_parsa)

# 5. In selectCharacter and initCharacterSelector, handle parsa
old_select_amirhossein = """  var btnAmirhossein = document.getElementById('btn_select_amirhossein');
  if (btnNima) btnNima.classList.remove('active');
  if (btnFargol) btnFargol.classList.remove('active');
  if (btnAli) btnAli.classList.remove('active');
  if (btnAmirhossein) btnAmirhossein.classList.remove('active');"""

new_select_parsa = """  var btnAmirhossein = document.getElementById('btn_select_amirhossein');
  var btnParsa = document.getElementById('btn_select_parsa');
  if (btnNima) btnNima.classList.remove('active');
  if (btnFargol) btnFargol.classList.remove('active');
  if (btnAli) btnAli.classList.remove('active');
  if (btnAmirhossein) btnAmirhossein.classList.remove('active');
  if (btnParsa) btnParsa.classList.remove('active');"""

patch = patch.replace(old_select_amirhossein, new_select_parsa)

old_active_amirhossein = """  } else if (charId === 'amirhossein') {
    if (btnAmirhossein) btnAmirhossein.classList.add('active');
  } else {"""

new_active_parsa = """  } else if (charId === 'amirhossein') {
    if (btnAmirhossein) btnAmirhossein.classList.add('active');
  } else if (charId === 'parsa') {
    if (btnParsa) btnParsa.classList.add('active');
  } else {"""

patch = patch.replace(old_active_amirhossein, new_active_parsa)

old_ta_amirhossein = """    } else if (charId === 'amirhossein') {
      if (tex_amirhossein_body) ta.texture = tex_amirhossein_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_amirhossein_died) x.texture = tex_amirhossein_died;
        x.width = 95;
        x.height = 111;
      }
    } else {"""

new_ta_parsa = """    } else if (charId === 'amirhossein') {
      if (tex_amirhossein_body) ta.texture = tex_amirhossein_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_amirhossein_died) x.texture = tex_amirhossein_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'parsa') {
      if (tex_parsa_body) ta.texture = tex_parsa_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_parsa_died) x.texture = tex_parsa_died;
        x.width = 95;
        x.height = 111;
      }
    } else {"""

patch = patch.replace(old_ta_amirhossein, new_ta_parsa)

old_sa_amirhossein = """    } else if (charId === 'amirhossein') {
      if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_amirhossein_died) w.texture = tex_amirhossein_died;
        w.width = 95;
        w.height = 111;
      }
    } else {"""

new_sa_parsa = """    } else if (charId === 'amirhossein') {
      if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_amirhossein_died) w.texture = tex_amirhossein_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'parsa') {
      if (tex_parsa_body) sa.texture = tex_parsa_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_parsa_died) w.texture = tex_parsa_died;
        w.width = 95;
        w.height = 111;
      }
    } else {"""

patch = patch.replace(old_sa_amirhossein, new_sa_parsa)

# initCharacterSelector
old_init_selector = """  var btnAmirhossein = document.getElementById('btn_select_amirhossein');
  
  if (btnNima) {"""

new_init_selector = """  var btnAmirhossein = document.getElementById('btn_select_amirhossein');
  var btnParsa = document.getElementById('btn_select_parsa');
  
  if (btnNima) {"""

patch = patch.replace(old_init_selector, new_init_selector)

old_init_listeners = """  if (btnAmirhossein) {
    btnAmirhossein.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      selectCharacter('amirhossein');
    });
  }

  // Set initial active state based on localStorage"""

new_init_listeners = """  if (btnAmirhossein) {
    btnAmirhossein.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      selectCharacter('amirhossein');
    });
  }
  if (btnParsa) {
    btnParsa.addEventListener('click', function(e) {
      e.stopPropagation();
      e.preventDefault();
      selectCharacter('parsa');
    });
  }

  // Set initial active state based on localStorage"""

patch = patch.replace(old_init_listeners, new_init_listeners)

old_init_active = """  if (btnAmirhossein) btnAmirhossein.classList.remove('active');
  if (selectedCharacter === 'fargol') {"""

new_init_active = """  if (btnAmirhossein) btnAmirhossein.classList.remove('active');
  if (btnParsa) btnParsa.classList.remove('active');
  if (selectedCharacter === 'fargol') {"""

patch = patch.replace(old_init_active, new_init_active)

old_init_check = """  } else if (selectedCharacter === 'amirhossein') {
    if (btnAmirhossein) btnAmirhossein.classList.add('active');
  } else {"""

new_init_check = """  } else if (selectedCharacter === 'amirhossein') {
    if (btnAmirhossein) btnAmirhossein.classList.add('active');
  } else if (selectedCharacter === 'parsa') {
    if (btnParsa) btnParsa.classList.add('active');
  } else {"""

patch = patch.replace(old_init_check, new_init_check)

# window.khanqahGame
old_khanqah_game = """  isAlive: function() { return typeof aa !== 'undefined' ? aa : false; },"""
new_khanqah_game = """  getParsaSleepCount: function() { return parsaSleepCount; },
  isParsaSleeping: function() { return parsaSleeping; },
  triggerParsaNap: triggerParsaNap,
  isAlive: function() { return typeof aa !== 'undefined' ? aa : false; },"""

patch = patch.replace(old_khanqah_game, new_khanqah_game)

# 6. Load textures in Xa
old_xa_images = """amirhossein_died:"images/amirhossein_died.png",bg_trees:"""
new_xa_images = """amirhossein_died:"images/amirhossein_died.png",parsa_body:"images/parsa_body.png",parsa_swing:"images/parsa_swing.png",parsa_sleep:"images/parsa_sleep.png",parsa_died:"images/parsa_died.png",bg_trees:"""
patch = patch.replace(old_xa_images, new_xa_images)

# Texture setup
old_tex_setup = """  tex_amirhossein_died = new b.Texture(new b.BaseTexture(a.amirhossein_died));"""
new_tex_setup = """  tex_amirhossein_died = new b.Texture(new b.BaseTexture(a.amirhossein_died));
  tex_parsa_body = new b.Texture(new b.BaseTexture(a.parsa_body));
  tex_parsa_swing = new b.Texture(new b.BaseTexture(a.parsa_swing));
  tex_parsa_sleep = new b.Texture(new b.BaseTexture(a.parsa_sleep));
  tex_parsa_died = new b.Texture(new b.BaseTexture(a.parsa_died));"""
patch = patch.replace(old_tex_setup, new_tex_setup)

# Sprite instantiations sa, ta, w, x
patch = patch.replace(
    ':(selectedCharacter==="amirhossein"?tex_amirhossein_body:tex_nima_old)',
    ':(selectedCharacter==="amirhossein"?tex_amirhossein_body:(selectedCharacter==="parsa"?tex_parsa_body:tex_nima_old))'
)
patch = patch.replace(
    ':(selectedCharacter==="amirhossein"?tex_amirhossein_died:tex_nima_died_old)',
    ':(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:tex_nima_died_old))'
)

# In pb()
old_pb_ali_reset = """  aliChops = 0;
  aliFlurryActive = false;
  aliFlurryRemaining = 0;"""

new_pb_ali_reset = """  aliChops = 0;
  aliFlurryActive = false;
  aliFlurryRemaining = 0;
  parsaSleepCount = 0;
  parsaSleeping = false;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }"""

patch = patch.replace(old_pb_ali_reset, new_pb_ali_reset)

old_pb_amirhossein = """    updateCharacterHUD('amirhossein', 'normal', 100, '۲X فعال', false);
  } else {"""

new_pb_parsa = """    updateCharacterHUD('amirhossein', 'normal', 100, '۲X فعال', false);
  } else if (selectedCharacter === 'parsa') {
    if (typeof sa !== 'undefined') {
      if (tex_parsa_body) sa.texture = tex_parsa_body;
      sa.width = 68;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_parsa_body) ta.texture = tex_parsa_body;
      ta.width = 68;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_parsa_died) w.texture = tex_parsa_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_parsa_died) x.texture = tex_parsa_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('parsa', 'normal', 100, '۲/۲ پتو', true);
  } else {"""

patch = patch.replace(old_pb_amirhossein, new_pb_parsa)

# In Ta()
old_ta_amirhossein = """    } else if (selectedCharacter === 'amirhossein') {
      updateCharacterHUD('amirhossein', 'normal', 100, '۲X فعال', false);
    } else {"""

new_ta_parsa = """    } else if (selectedCharacter === 'amirhossein') {
      updateCharacterHUD('amirhossein', 'normal', 100, '۲X فعال', false);
    } else if (selectedCharacter === 'parsa') {
      var remB = Math.max(0, 2 - parsaSleepCount);
      if (parsaSleeping) {
        ba = +new Date + qa; // Stamina held at max during nap
        updateCharacterHUD('parsa', 'sleep', (remB / 2) * 100, remB + '/2 پتو', false);
      } else {
        updateCharacterHUD('parsa', 'normal', (remB / 2) * 100, remB + '/2 پتو', false);
      }
    } else {"""

patch = patch.replace(old_ta_amirhossein, new_ta_parsa)

# In Ca(a):
old_ca_pre = """  if (aa && selectedCharacter === 'ali' && aliFlurryActive) {
    za || (za = !0, ba = +new Date + 4250);
    var b_ali = da[0];
    if (b_ali && a === (0 > b_ali)) {
      // FLURRY PROTECTION: Cleave branch safely without dying!
      1 == Math.abs(b_ali) && $a(a, !0);
      da[0] = 0;
    }
  }"""

new_ca_pre = """  if (aa && selectedCharacter === 'ali' && aliFlurryActive) {
    za || (za = !0, ba = +new Date + 4250);
    var b_ali = da[0];
    if (b_ali && a === (0 > b_ali)) {
      // FLURRY PROTECTION: Cleave branch safely without dying!
      1 == Math.abs(b_ali) && $a(a, !0);
      da[0] = 0;
    }
  }
  if (aa && selectedCharacter === 'parsa' && parsaSleeping) {
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

patch = patch.replace(old_ca_pre, new_ca_pre)

# In chop score branch
old_ca_score = """    } else if (selectedCharacter === 'amirhossein') {
      ca++;
      ca % 20 || (Ha++, nb());
      Fa();
      spawnCombatPopup('⚡ ۲X امتیاز! +2', 'crit');
      triggerTelegramHaptic('medium');
    } else {"""

new_ca_score = """    } else if (selectedCharacter === 'amirhossein') {
      ca++;
      ca % 20 || (Ha++, nb());
      Fa();
      spawnCombatPopup('⚡ ۲X امتیاز! +2', 'crit');
      triggerTelegramHaptic('medium');
    } else if (selectedCharacter === 'parsa') {
      triggerTelegramHaptic('light');
    } else {"""

patch = patch.replace(old_ca_score, new_ca_score)

# In Va()
old_va_pre = """  aliFlurryActive = false;
  aliFlurryRemaining = 0;"""

new_va_pre = """  aliFlurryActive = false;
  aliFlurryRemaining = 0;
  parsaSleeping = false;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }"""

patch = patch.replace(old_va_pre, new_va_pre)

old_va_death_tex = """(selectedCharacter === 'amirhossein' ? tex_amirhossein_died : (nimaPhase === 'young' ? tex_nima_died_young : tex_nima_died_old))"""
new_va_death_tex = """(selectedCharacter === 'amirhossein' ? tex_amirhossein_died : (selectedCharacter === 'parsa' ? tex_parsa_died : (nimaPhase === 'young' ? tex_nima_died_young : tex_nima_died_old)))"""
patch = patch.replace(old_va_death_tex, new_va_death_tex)

# In wa()
old_wa_tex = """(selectedCharacter==="amirhossein"?tex_amirhossein_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old))"""
new_wa_tex = """(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old)))"""
patch = patch.replace(old_wa_tex, new_wa_tex)

# In mb(a) swing
old_mb_amirhossein = """  } else if (selectedCharacter === 'amirhossein') {
    if (typeof sa !== 'undefined') {
      if (tex_amirhossein_swing) {
        sa.texture = tex_amirhossein_swing;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else {"""

new_mb_parsa = """  } else if (selectedCharacter === 'amirhossein') {
    if (typeof sa !== 'undefined') {
      if (tex_amirhossein_swing) {
        sa.texture = tex_amirhossein_swing;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else if (selectedCharacter === 'parsa') {
    if (typeof sa !== 'undefined') {
      if (tex_parsa_swing) {
        sa.texture = tex_parsa_swing;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          if (tex_parsa_body) sa.texture = (parsaSleeping && tex_parsa_sleep ? tex_parsa_sleep : tex_parsa_body);
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else {"""

patch = patch.replace(old_mb_amirhossein, new_mb_parsa)

# In rb() and Ia()
patch = patch.replace(
    'x.texture = (selectedCharacter==="fargol"?tex_fargol_died:(selectedCharacter==="ali"?tex_ali_died:(selectedCharacter==="amirhossein"?tex_amirhossein_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old))))||x.texture;',
    'x.texture = (selectedCharacter==="fargol"?tex_fargol_died:(selectedCharacter==="ali"?tex_ali_died:(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old)))))||x.texture;'
)
patch = patch.replace(
    'ta.texture = (selectedCharacter === \'fargol\' ? tex_fargol_normal : (selectedCharacter === \'ali\' ? tex_ali_body : (selectedCharacter === \'amirhossein\' ? tex_amirhossein_body : tex_nima_old))) || ta.texture;',
    'ta.texture = (selectedCharacter === \'fargol\' ? tex_fargol_normal : (selectedCharacter === \'ali\' ? tex_ali_body : (selectedCharacter === \'amirhossein\' ? tex_amirhossein_body : (selectedCharacter === \'parsa\' ? tex_parsa_body : tex_nima_old)))) || ta.texture;'
)
patch = patch.replace(
    'x.texture = (selectedCharacter === \'fargol\' ? tex_fargol_died : (selectedCharacter === \'ali\' ? tex_ali_died : (selectedCharacter === \'amirhossein\' ? tex_amirhossein_died : tex_nima_died_old))) || x.texture;',
    'x.texture = (selectedCharacter === \'fargol\' ? tex_fargol_died : (selectedCharacter === \'ali\' ? tex_ali_died : (selectedCharacter === \'amirhossein\' ? tex_amirhossein_died : (selectedCharacter === \'parsa\' ? tex_parsa_died : tex_nima_died_old)))) || x.texture;'
)

# Intercept stamina timeout in Ta():
# orig_main.js has: 0<ba-+new Date?Ua():Va()
# We intercept tiredness exhaustion for Parsa!
stamina_intercept_code = """
# Intercept stamina exhaustion for Parsa's Blanket Sleep
code = code.replace(
    '0<ba-+new Date?Ua():Va()',
    '0<ba-+new Date?Ua():(selectedCharacter==="parsa"&&parsaSleepCount<2?triggerParsaNap():Va())'
)
"""

if 'stamina_intercept_code' not in patch:
    # Insert before with open('public/js/main.js'
    idx = patch.rfind("with open('public/js/main.js'")
    patch = patch[:idx] + stamina_intercept_code + "\n" + patch[idx:]

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(patch)

print('Updated scratch/patch_lumberjack.py successfully!')
