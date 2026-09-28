with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ahmad translations
content = content.replace(
    "spawnCombatPopup('🛡️ Shield Broke & Saved! (' + ahmadShieldCount + ' Left) 💥', 'crit');",
    "spawnCombatPopup('🛡️ سپر شکست و جان سالم به در برد! (' + ahmadShieldCount + ' باقی‌مانده) 💥', 'crit');"
)
content = content.replace(
    "spawnCombatPopup('🛡️ Last Shield Saved Ahmad! 💥', 'crit');",
    "spawnCombatPopup('🛡️ آخرین سپر احمد را نجات داد! 💥', 'crit');"
)
content = content.replace(
    "spawnCombatPopup('🛡️ New Shield Stacked! (' + ahmadShieldCount + ' Total) 🛡️', 'crit');",
    "spawnCombatPopup('🛡️ سپر جدید اضافه شد! (' + ahmadShieldCount + ' سپر) 🛡️', 'crit');"
)
content = content.replace(
    "spawnCombatPopup('🛡️ Ahmad Shield Activated! 🛡️', 'crit');",
    "spawnCombatPopup('🛡️ سپر احمد فعال شد! 🛡️', 'crit');"
)

# Erfan translations
content = content.replace(
    "spawnCombatPopup('⚡ 3X Critical Score! +3', 'crit');",
    "spawnCombatPopup('⚡ امتیاز ۳ برابر! +3', 'crit');"
)

# Parsa smaller popups
content = content.replace(
    "spawnCombatPopup('🛌 خواب ۳ ثانیه‌ای! تجدید قوا (' + parsaSleepCount + '/2) 💤', 'crit');",
    "spawnCombatPopup('🛌 خواب ۳ ثانیه‌ای! تجدید قوا (' + parsaSleepCount + '/2) 💤', 'crit small-popup');"
)
content = content.replace(
    "spawnCombatPopup('⏰ بیدار شد! آماده برای تبر زدن! 🪓', 'young');",
    "spawnCombatPopup('⏰ بیدار شد! آماده برای تبر زدن! 🪓', 'young small-popup');"
)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated popups in patch_lumberjack.py")
