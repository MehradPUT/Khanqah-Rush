import re

with open('scratch/patch_lumberjack.py', 'r') as f:
    content = f.read()

# 1. Update char-hud-name for Fargol
content = content.replace(
    "nameEl.innerText = (phase === 'flame' ? '🔥 fargol' : '👑 fargol');",
    "nameEl.innerText = (phase === 'flame' ? '🔥 Sultan' : '👑 Sultan');"
)

# 2. Remove Sultan Flame popups
content = content.replace("spawnCombatPopup('🔥 Sultan Flame! Invincible! 🔥', 'crit small-popup');", "// spawnCombatPopup removed")
content = content.replace("spawnCombatPopup('💥 Shattered! (Sultan) 💥', 'crit small-popup');", "// spawnCombatPopup removed")

# 3. Fix chop counting during phase 2
# We need to replace the logic in Ca(a)
old_logic = """    if (selectedCharacter === 'fargol') {
      fargolChops++;
      if (fargolChops > 0 && fargolChops % 100 === 0) {"""

new_logic = """    if (selectedCharacter === 'fargol') {
      if (!fargolFlameActive) {
        fargolChops++;
      }
      if (!fargolFlameActive && fargolChops > 0 && fargolChops % 100 === 0) {"""
      
content = content.replace(old_logic, new_logic)

with open('scratch/patch_lumberjack.py', 'w') as f:
    f.write(content)
print("Updated patch_lumberjack.py")
