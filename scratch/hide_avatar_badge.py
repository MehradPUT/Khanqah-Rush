with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Hide avatar
code = code.replace(
    '.char-card-avatar {\n      font-size: 24px;\n      line-height: 1;\n      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));\n    }',
    '.char-card-avatar {\n      display: none !important;\n      font-size: 24px;\n      line-height: 1;\n      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));\n    }'
)

# Hide badge
code = code.replace(
    '.char-card-badge {\n      font-family: \'Vazirmatn\', sans-serif;',
    '.char-card-badge { display: none !important;\n      font-family: \'Vazirmatn\', sans-serif;'
)

# Center the name now that it's alone
code = code.replace(
    '.char-card-titles {\n      display: flex;\n      align-items: center;\n      gap: 6px;\n      flex-wrap: wrap;\n    }',
    '.char-card-titles {\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      width: 100%;\n      gap: 6px;\n      flex-wrap: wrap;\n    }'
)

code = code.replace(
    '.char-card-header {\n      display: flex;\n      align-items: center;\n      gap: 8px;\n    }',
    '.char-card-header {\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      width: 100%;\n      gap: 8px;\n    }'
)

code = code.replace(
    '.char-card-name {\n      font-family: \'Arial Black\', Impact, sans-serif;\n      font-size: 15px;',
    '.char-card-name {\n      font-family: \'Arial Black\', Impact, sans-serif;\n      font-size: 17px;\n      text-align: center;'
)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Avatar and badge hidden.")
