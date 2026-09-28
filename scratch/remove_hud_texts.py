with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_html = """    barWrap.innerHTML = `
      <div class="char-hud-row">
        <span class="char-hud-name" id="char_hud_name">nima</span>
        <span class="char-hud-shield" id="char_hud_shield" style="display:none;">🛡️ جان دوم</span>
      </div>
      <div class="char-hud-header">
        <span class="char-hud-title" id="char_hud_title">جوانی</span>
        <span class="char-hud-timer" id="char_hud_timer">15s</span>
      </div>
      <div class="char-hud-track">
        <div class="char-hud-fill" id="char_hud_fill"></div>
      </div>
    `;"""

new_html = """    barWrap.innerHTML = `
      <div class="char-hud-header" style="justify-content: flex-end; margin-bottom: 4px;">
        <span class="char-hud-timer" id="char_hud_timer">15s</span>
      </div>
      <div class="char-hud-track">
        <div class="char-hud-fill" id="char_hud_fill"></div>
      </div>
    `;"""

code = code.replace(old_html, new_html)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("HUD texts removed.")
