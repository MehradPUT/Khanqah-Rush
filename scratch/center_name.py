with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Make char-card-name absolute block center
code = code.replace(
    '.char-card-name {\n      font-family: \'Arial Black\', Impact, sans-serif;\n      font-size: 17px;\n      text-align: center;\n      font-weight: 900;\n      letter-spacing: 0.5px;\n      color: #ffffff;\n    }',
    '.char-card-name {\n      font-family: \'Arial Black\', Impact, sans-serif;\n      font-size: 17px;\n      text-align: center;\n      font-weight: 900;\n      letter-spacing: 0.5px;\n      color: #ffffff;\n      display: block;\n      width: 100%;\n      margin: 0 auto;\n      direction: ltr;\n    }'
)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Name centering applied.")
