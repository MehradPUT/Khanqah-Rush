with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Modify the popup content and type
old_erfan_popup = "spawnCombatPopup('⚡ امتیاز ۳ برابر! +3', 'crit');"
new_erfan_popup = "spawnCombatPopup('3X', 'erfan-crit');"
code = code.replace(old_erfan_popup, new_erfan_popup)

# Modify spawnCombatPopup to handle 'erfan-crit' positioning
old_spawn_func = """  var x = window.innerWidth / 2 + (Math.random() * 40 - 20);
  var y = window.innerHeight * 0.42 + (Math.random() * 30 - 15);
  el.style.left = x + 'px';
  el.style.top = y + 'px';"""

new_spawn_func = """  if (type === 'erfan-crit') {
    var x = window.innerWidth - 60 + (Math.random() * 20 - 10);
    var y = 60 + (Math.random() * 30 - 15);
    el.style.left = x + 'px';
    el.style.top = y + 'px';
  } else {
    var x = window.innerWidth / 2 + (Math.random() * 40 - 20);
    var y = window.innerHeight * 0.42 + (Math.random() * 30 - 15);
    el.style.left = x + 'px';
    el.style.top = y + 'px';
  }"""
code = code.replace(old_spawn_func, new_spawn_func)

# Add CSS for .erfan-crit
old_css = ".arcade-combat-text.crit {\n      color: #ffca28;"
new_css = ".arcade-combat-text.erfan-crit {\n      color: #f39c12;\n      text-shadow: 0 0 10px #f1c40f, 0 0 20px #e74c3c, 2px 2px 0px #000;\n      font-size: 32px;\n      font-weight: 900;\n    }\n    .arcade-combat-text.crit {\n      color: #ffca28;"

code = code.replace(old_css, new_css)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Erfan popup replaced with 3X and moved to top right.")
