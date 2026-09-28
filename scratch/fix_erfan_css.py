with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_css = ".arcade-combat-text.crit {"
new_css = ".arcade-combat-text.erfan-crit { color: #f39c12; text-shadow: 0 0 10px #f1c40f, 0 0 20px #e74c3c, 2px 2px 0px #000; font-size: 32px; font-weight: 900; }\n    .arcade-combat-text.crit {"

code = code.replace(old_css, new_css)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("CSS Fixed")
