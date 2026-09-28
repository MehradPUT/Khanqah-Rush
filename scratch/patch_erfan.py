import re
import sys

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. State declarations
    if 'var tex_erfan_body = null;' not in code:
        code = code.replace(
            'var tex_ahmad_body = null;\nvar tex_ahmad_swing = null;\nvar tex_ahmad_died = null;',
            'var tex_ahmad_body = null;\nvar tex_ahmad_swing = null;\nvar tex_ahmad_died = null;\nvar tex_erfan_body = null;\nvar tex_erfan_swing = null;\nvar tex_erfan_died = null;'
        )

    # 2. CSS for Erfan
    erfan_tab_css = """    .char-tab-btn.active[data-char="ahmad"] .char-tab-badge {
      color: #5dade2;
    }

    .char-tab-btn.active[data-char="erfan"] {
      background: linear-gradient(135deg, rgba(43, 92, 143, 0.4) 0%, rgba(243, 156, 18, 0.25) 100%);
      border-color: #f39c12;
      box-shadow: 0 0 14px rgba(243, 156, 18, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.4);
    }

    .char-tab-btn.active[data-char="erfan"] .char-tab-badge {
      color: #f39c12;
    }"""
    if '.char-tab-btn.active[data-char="erfan"]' not in code:
        code = code.replace(
            """    .char-tab-btn.active[data-char="ahmad"] .char-tab-badge {
      color: #5dade2;
    }""",
            erfan_tab_css
        )

    erfan_hud_css = """    .char-ability-bar-wrap.ahmad .char-hud-fill {
      background: linear-gradient(90deg, #2980b9 0%, #3498db 70%, #5dade2 100%);
      box-shadow: 0 0 8px rgba(52, 152, 219, 0.7);
    }

    .char-ability-bar-wrap.erfan.normal {
      background: rgba(18, 28, 42, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(43, 92, 143, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(43, 92, 143, 0.3);
    }

    .char-ability-bar-wrap.erfan.active {
      background: rgba(45, 25, 10, 0.94);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid #f39c12;
      box-shadow: 0 0 18px rgba(243, 156, 18, 0.85), 0 0 10px rgba(231, 76, 60, 0.6);
      animation: fargolFlamePulse 0.6s infinite ease-in-out;
    }

    .char-ability-bar-wrap.erfan.active .char-hud-title {
      color: #f39c12;
      text-shadow: 0 0 6px rgba(243, 156, 18, 0.9);
    }

    .char-ability-bar-wrap.erfan.active .char-hud-timer {
      color: #f1c40f;
      text-shadow: 0 0 6px rgba(241, 196, 15, 0.9);
    }

    .char-ability-bar-wrap.erfan.active .char-hud-fill {
      background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #f1c40f 100%);
      box-shadow: 0 0 10px rgba(243, 156, 18, 0.9);
    }

    .char-ability-bar-wrap.erfan.normal .char-hud-timer {
      color: #5dade2;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.erfan .char-hud-fill {
      background: linear-gradient(90deg, #2b5c8f 0%, #3498db 70%, #5dade2 100%);
      box-shadow: 0 0 8px rgba(43, 92, 143, 0.7);
    }"""
    if '.char-ability-bar-wrap.erfan' not in code:
        code = code.replace(
            """    .char-ability-bar-wrap.ahmad .char-hud-fill {
      background: linear-gradient(90deg, #2980b9 0%, #3498db 70%, #5dade2 100%);
      box-shadow: 0 0 8px rgba(52, 152, 219, 0.7);
    }""",
            erfan_hud_css
        )

    # 3. updateCharacterHUD for erfan
    erfan_hud_logic = """  } else if (charId === 'ahmad') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      shieldEl.innerText = ahmadShieldCount > 0 ? ('🛡️ ' + ahmadShieldCount + ' سپر') : '🛡️ سپر ۱۰۰';
      shieldEl.className = 'char-hud-shield ' + (ahmadShieldCount > 0 ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = ahmadShieldCount > 0 ? ('🛡️ ahmad (سپر: ' + ahmadShieldCount + ')') : '🛡️ ahmad';
    }
    if (titleEl) {
      titleEl.innerText = ahmadShieldCount > 0 ? ('سپر فعال (' + ahmadShieldCount + ' عدد)') : 'شارژ سپر (۱۰۰ ضربه)';
    }
  } else if (charId === 'erfan') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      shieldEl.innerText = phase === 'active' ? '⚡ ۳X فعال' : '⚡ ۳X آماده';
      shieldEl.className = 'char-hud-shield ' + (phase === 'active' ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = phase === 'active' ? '⚡ erfan (۳X امتیاز)' : '⚡ erfan';
    }
    if (titleEl) {
      titleEl.innerText = phase === 'active' ? 'امتیاز ۳ برابر بحرانی! 🔥' : 'خستگی زیر ۵۰٪ = ۳X امتیاز';
    }"""
    if "else if (charId === 'erfan')" not in code:
        code = code.replace(
            """  } else if (charId === 'ahmad') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      shieldEl.innerText = ahmadShieldCount > 0 ? ('🛡️ ' + ahmadShieldCount + ' سپر') : '🛡️ سپر ۱۰۰';
      shieldEl.className = 'char-hud-shield ' + (ahmadShieldCount > 0 ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = ahmadShieldCount > 0 ? ('🛡️ ahmad (سپر: ' + ahmadShieldCount + ')') : '🛡️ ahmad';
    }
    if (titleEl) {
      titleEl.innerText = ahmadShieldCount > 0 ? ('سپر فعال (' + ahmadShieldCount + ' عدد)') : 'شارژ سپر (۱۰۰ ضربه)';
    }""",
            erfan_hud_logic
        )

    # 4. Button listeners in initCharacterSelector()
    btn_listener = """  var btnAhmad = document.getElementById('btn_select_ahmad');
  if (btnAhmad) {
    btnAhmad.addEventListener('click', function(e) {
      e.stopPropagation();
      selectCharacter('ahmad');
    });
  }
  var btnErfan = document.getElementById('btn_select_erfan');
  if (btnErfan) {
    btnErfan.addEventListener('click', function(e) {
      e.stopPropagation();
      selectCharacter('erfan');
    });
  }"""
    if "var btnErfan = document.getElementById('btn_select_erfan');" not in code:
        code = code.replace(
            """  var btnAhmad = document.getElementById('btn_select_ahmad');
  if (btnAhmad) {
    btnAhmad.addEventListener('click', function(e) {
      e.stopPropagation();
      selectCharacter('ahmad');
    });
  }""",
            btn_listener
        )

    # 5. selectCharacter tab toggles
    tab_toggles = """  var btnParsa = document.getElementById('btn_select_parsa');
  var btnAhmad = document.getElementById('btn_select_ahmad');
  var btnErfan = document.getElementById('btn_select_erfan');"""
    if "var btnErfan = document.getElementById('btn_select_erfan');" not in code:
        code = code.replace(
            """  var btnParsa = document.getElementById('btn_select_parsa');
  var btnAhmad = document.getElementById('btn_select_ahmad');""",
            tab_toggles
        )
    if 'if (btnErfan) btnErfan.classList.remove(\'active\');' not in code:
        code = code.replace(
            'if (btnAhmad) btnAhmad.classList.remove(\'active\');',
            'if (btnAhmad) btnAhmad.classList.remove(\'active\');\n  if (btnErfan) btnErfan.classList.remove(\'active\');'
        )

    select_tab_branch = """  } else if (charId === 'ahmad') {
    if (btnAhmad) btnAhmad.classList.add('active');
  } else if (charId === 'erfan') {
    if (btnErfan) btnErfan.classList.add('active');"""
    if "else if (charId === 'erfan') {\n    if (btnErfan) btnErfan.classList.add('active');" not in code:
        code = code.replace(
            """  } else if (charId === 'ahmad') {
    if (btnAhmad) btnAhmad.classList.add('active');""",
            select_tab_branch
        )

    # selectCharacter preview texture updates
    ta_branch = """    } else if (charId === 'ahmad') {
      if (tex_ahmad_body) ta.texture = tex_ahmad_body;
      ta.width = 94;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_ahmad_died) x.texture = tex_ahmad_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'erfan') {
      if (tex_erfan_body) ta.texture = tex_erfan_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_erfan_died) x.texture = tex_erfan_died;
        x.width = 95;
        x.height = 111;
      }"""
    if "else if (charId === 'erfan') {\n      if (tex_erfan_body) ta.texture = tex_erfan_body;" not in code:
        code = code.replace(
            """    } else if (charId === 'ahmad') {
      if (tex_ahmad_body) ta.texture = tex_ahmad_body;
      ta.width = 94;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_ahmad_died) x.texture = tex_ahmad_died;
        x.width = 95;
        x.height = 111;
      }""",
            ta_branch
        )

    sa_branch = """    } else if (charId === 'ahmad') {
      if (tex_ahmad_body) sa.texture = tex_ahmad_body;
      sa.width = 94;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_ahmad_died) w.texture = tex_ahmad_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'erfan') {
      if (tex_erfan_body) sa.texture = tex_erfan_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_erfan_died) w.texture = tex_erfan_died;
        w.width = 95;
        w.height = 111;
      }"""
    if "else if (charId === 'erfan') {\n      if (tex_erfan_body) sa.texture = tex_erfan_body;" not in code:
        code = code.replace(
            """    } else if (charId === 'ahmad') {
      if (tex_ahmad_body) sa.texture = tex_ahmad_body;
      sa.width = 94;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_ahmad_died) w.texture = tex_ahmad_died;
        w.width = 95;
        w.height = 111;
      }""",
            sa_branch
        )

    # 6. Helper API
    if 'isErfanClutch' not in code:
        code = code.replace(
            '  setAhmadShield: function(b) { ahmadShieldCount = b ? 1 : 0; ahmadShieldActive = b; },',
            '  setAhmadShield: function(b) { ahmadShieldCount = b ? 1 : 0; ahmadShieldActive = b; },\n  isErfanClutch: function() { return selectedCharacter === "erfan" && ((ba - +new Date) / qa < 0.5); },'
        )

    # 7. Game loop Ta() HUD updater
    ta_hud_update = """    } else if (selectedCharacter === 'ahmad') {
      var ahmProg = ahmadChops % 100;
      updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);
    } else if (selectedCharacter === 'erfan') {
      var curStaminaRatio = Math.max(0, Math.min(1, (ba - +new Date) / qa));
      var isClutch = curStaminaRatio < 0.5;
      updateCharacterHUD('erfan', isClutch ? 'active' : 'normal', curStaminaRatio * 100, isClutch ? '۳X فعال! 🔥' : Math.round(curStaminaRatio * 100) + '%', isClutch);"""
    if "else if (selectedCharacter === 'erfan')" not in code:
        code = code.replace(
            """    } else if (selectedCharacter === 'ahmad') {
      var ahmProg = ahmadChops % 100;
      updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);""",
            ta_hud_update
        )

    # 8. mb(a) swing animation for Erfan
    mb_erfan = """  } else if (selectedCharacter === 'ahmad') {
    if (typeof sa !== 'undefined') {
      if (tex_ahmad_swing) {
        sa.texture = tex_ahmad_swing;
        sa.width = 120;
        sa.height = 140;
      }
      setTimeout(function(){ 
        if (typeof sa !== 'undefined') {
          if (tex_ahmad_body) sa.texture = tex_ahmad_body;
          sa.width = 94; 
          sa.height = 140;
        }
      }, 65);
    }
  } else if (selectedCharacter === 'erfan') {
    if (typeof sa !== 'undefined') {
      if (tex_erfan_swing) {
        sa.texture = tex_erfan_swing;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){ 
        if (typeof sa !== 'undefined') {
          if (tex_erfan_body) sa.texture = tex_erfan_body;
          sa.width = 68; 
          sa.height = 140;
        }
      }, 65);
    }
  }"""
    if "else if (selectedCharacter === 'erfan') {\n    if (typeof sa !== 'undefined') {\n      if (tex_erfan_swing)" not in code:
        code = code.replace(
            """  } else if (selectedCharacter === 'ahmad') {
    if (typeof sa !== 'undefined') {
      if (tex_ahmad_swing) {
        sa.texture = tex_ahmad_swing;
        sa.width = 120;
        sa.height = 140;
      }
      setTimeout(function(){ 
        if (typeof sa !== 'undefined') {
          if (tex_ahmad_body) sa.texture = tex_ahmad_body;
          sa.width = 94; 
          sa.height = 140;
        }
      }, 65);
    }
  }""",
            mb_erfan
        )

    # 9. pb() reset
    pb_erfan = """  if (selectedCharacter === 'ahmad') {
    if (typeof sa !== 'undefined') {
      if (tex_ahmad_body) sa.texture = tex_ahmad_body;
      sa.width = 94;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_ahmad_body) ta.texture = tex_ahmad_body;
      ta.width = 94;
      ta.height = 140;
    }
  } else if (selectedCharacter === 'erfan') {
    if (typeof sa !== 'undefined') {
      if (tex_erfan_body) sa.texture = tex_erfan_body;
      sa.width = 68;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_erfan_body) ta.texture = tex_erfan_body;
      ta.width = 68;
      ta.height = 140;
    }
  }"""
    if "else if (selectedCharacter === 'erfan') {\n    if (typeof sa !== 'undefined') {\n      if (tex_erfan_body) sa.texture = tex_erfan_body;\n      sa.width = 68;" not in code:
        code = code.replace(
            """  if (selectedCharacter === 'ahmad') {
    if (typeof sa !== 'undefined') {
      if (tex_ahmad_body) sa.texture = tex_ahmad_body;
      sa.width = 94;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_ahmad_body) ta.texture = tex_ahmad_body;
      ta.width = 94;
      ta.height = 140;
    }
  }""",
            pb_erfan
        )

    # 10. Ca(a) chop cut logic
    chop_erfan = """      } else {
        triggerTelegramHaptic('light');
        var ahmProg = ahmadChops % 100;
        updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);
      }
    } else if (selectedCharacter === 'erfan') {
      var curStaminaRatio = (ba - +new Date) / qa;
      if (curStaminaRatio < 0.5) {
        ca += 2;
        ca % 20 || (Ha++, nb());
        Fa();
        spawnCombatPopup('⚡ ۳X امتیاز بحرانی! +3', 'crit');
        triggerTelegramHaptic('heavy');
      } else {
        triggerTelegramHaptic('light');
      }"""
    if "else if (selectedCharacter === 'erfan') {\n      var curStaminaRatio = (ba - +new Date) / qa;\n      if (curStaminaRatio < 0.5) {" not in code:
        code = code.replace(
            """      } else {
        triggerTelegramHaptic('light');
        var ahmProg = ahmadChops % 100;
        updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);
      }""",
            chop_erfan
        )

    # 11. Xa({...}) preloader assets
    if 'erfan_body:' not in code:
        code = code.replace(
            'ahmad_died:"images/ahmad_died.png"',
            'ahmad_died:"images/ahmad_died.png",erfan_body:"images/erfan_body.png",erfan_swing:"images/erfan_swing.png",erfan_died:"images/erfan_died.png"'
        )

    # 12. Texture creation
    if 'tex_erfan_body = new b.Texture' not in code:
        code = code.replace(
            'tex_ahmad_died = new b.Texture(new b.BaseTexture(a.ahmad_died));',
            'tex_ahmad_died = new b.Texture(new b.BaseTexture(a.ahmad_died));\n  tex_erfan_body = new b.Texture(new b.BaseTexture(a.erfan_body));\n  tex_erfan_swing = new b.Texture(new b.BaseTexture(a.erfan_swing));\n  tex_erfan_died = new b.Texture(new b.BaseTexture(a.erfan_died));'
        )

    # 13. Ternaries for sa, ta, w, x
    # sa
    code = code.replace(
        'selectedCharacter==="ahmad"?tex_ahmad_body:tex_nima_old',
        'selectedCharacter==="ahmad"?tex_ahmad_body:(selectedCharacter==="erfan"?tex_erfan_body:tex_nima_old)'
    )
    # w and x
    code = code.replace(
        'selectedCharacter==="ahmad"?tex_ahmad_died:tex_nima_died_old',
        'selectedCharacter==="ahmad"?tex_ahmad_died:(selectedCharacter==="erfan"?tex_erfan_died:tex_nima_died_old)'
    )
    code = code.replace(
        'selectedCharacter==="ahmad"?tex_ahmad_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old)',
        'selectedCharacter==="ahmad"?tex_ahmad_died:(selectedCharacter==="erfan"?tex_erfan_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old))'
    )
    # Ia() ta texture
    code = code.replace(
        'selectedCharacter === \'ahmad\' ? tex_ahmad_body : tex_nima_old',
        'selectedCharacter === \'ahmad\' ? tex_ahmad_body : (selectedCharacter === \'erfan\' ? tex_erfan_body : tex_nima_old)'
    )
    # Ia() x texture
    code = code.replace(
        'selectedCharacter === \'ahmad\' ? tex_ahmad_died : tex_nima_died_old',
        'selectedCharacter === \'ahmad\' ? tex_ahmad_died : (selectedCharacter === \'erfan\' ? tex_erfan_died : tex_nima_died_old)'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"Successfully patched {filepath}!")

patch_file('public/js/main.js')
