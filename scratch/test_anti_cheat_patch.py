import re

with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    patch = f.read()

# Verify presence of all key anchors
assert 'window.khanqahGame = {' in patch
assert "ca_pattern = r'function Ca\(a\)\s*\{'" in patch
assert 'wa(a,!0,2==Math.abs(b))\x27\x27\x27' in patch
assert "old_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):Z&&!h||32!=a||(Ka(La),fb())'" in patch
print("All patch anchors verified successfully!")
