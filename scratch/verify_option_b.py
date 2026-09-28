import os
import re
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'

# --- 1. Code Validation ---
with open('public/js/main.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

# Check for presence of Option B dimensions
checks = [
    ('sa.width = 115', 'sa.width = 115' in js_code),
    ('sa.height = 140', 'sa.height = 140' in js_code),
    ('ta.width = 86', 'ta.width = 86' in js_code),
    ('ta.width = 68', 'ta.width = 68' in js_code),
    ('ta.height = 140', 'ta.height = 140' in js_code),
    ('w.width = 95', 'w.width = 95' in js_code or 'w.width=95' in js_code),
    ('w.height = 111', 'w.height = 111' in js_code or 'w.height=111' in js_code),
    ('x.width = 95', 'x.width = 95' in js_code or 'x.width=95' in js_code),
    ('x.height = 111', 'x.height = 111' in js_code or 'x.height=111' in js_code),
    ('Flame 107x142', 'sa.width = 107' in js_code and 'sa.height = 142' in js_code),
]

all_passed = True
for name, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if not passed:
        all_passed = False

if not all_passed:
    raise RuntimeError("Verification failed: Not all Option B invariants were found in public/js/main.js")

print("All code checks passed!")

# --- 2. Generate In-Game Comparison Showcase Image ---
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 16)
font_label = ImageFont.truetype(font_path, 12)
font_badge = ImageFont.truetype(font_path, 11)

chars = [
    ('Nima (Old)', 'public/images/nima_body_old.png', 68, 140, '⚡ جوانی'),
    ('Fargol (Sultan)', 'public/images/fargol_body.png', 86, 140, '🔥 سلطان'),
    ('Ali (Architect)', 'public/images/ali_body.png', 68, 140, '🪓 رگبار ۱۰'),
    ('Amirhossein', 'public/images/amirhossein_body.png', 68, 140, '⚡ ۲X امتیاز'),
]

w, h = 880, 480
card = Image.new('RGBA', (w, h), (18, 26, 42, 255))
draw = ImageDraw.Draw(card)

# Title Header
draw.rectangle([0, 0, w, 60], fill=(13, 20, 32, 255))
draw.line([(0, 60), (w, 60)], fill=(41, 128, 185, 200), width=2)
draw.text((25, 18), "Khanqah Rush - Option B (+30.8% / 140px Height) In-Game Heroic Scale", font=font_title, fill=(255, 215, 0, 255))

panel_w = w // 4

for i, (name, img_path, spr_w, spr_h, badge) in enumerate(chars):
    px = i * panel_w
    # Sky backdrop
    for y in range(61, 410):
        ratio = (y - 61) / (410 - 61)
        r = int(24 + (130 - 24) * ratio)
        g = int(45 + (180 - 45) * ratio)
        b = int(75 + (160 - 75) * ratio)
        draw.line([(px, y), (px + panel_w, y)], fill=(r, g, b, 255))

    # Tree trunk
    tx1 = px + panel_w - 65
    tx2 = tx1 + 55
    draw.rectangle([tx1, 61, tx2, 410], fill=(125, 90, 45, 255))
    for ty in range(80, 410, 40):
        draw.line([(tx1 + 5, ty), (tx1 + 45, ty)], fill=(95, 65, 28, 255), width=2)

    # Ground line
    draw.rectangle([px, 410, px + panel_w, h], fill=(115, 168, 70, 255))
    draw.line([(px, 410), (px + panel_w, 410)], fill=(90, 140, 50, 255), width=3)

    # Character Sprite
    raw_img = Image.open(img_path).convert('RGBA')
    scaled_img = raw_img.resize((spr_w, spr_h), Image.Resampling.LANCZOS)
    
    char_x = tx1 - spr_w - 6
    char_y = 410 - spr_h
    card.paste(scaled_img, (char_x, char_y), scaled_img)

    # Dimension tag
    draw.rounded_rectangle([px + 12, 75, px + panel_w - 12, 105], radius=6, fill=(13, 20, 32, 220), outline=(41, 128, 185, 220), width=1)
    draw.text((px + 20, 82), f"{name}", font=font_label, fill=(255, 255, 255, 255))
    
    # Size badge
    draw.rounded_rectangle([px + 12, 425, px + panel_w - 12, 465], radius=8, fill=(13, 20, 32, 230), outline=(255, 215, 0, 180), width=1)
    draw.text((px + 22, 432), f"Size: {spr_w}x{spr_h}px (Option B)", font=font_badge, fill=(255, 215, 0, 255))
    draw.text((px + 22, 448), f"Power: {badge}", font=font_badge, fill=(112, 161, 255, 255))

    # Divider line
    if i > 0:
        draw.line([(px, 60), (px, h)], fill=(41, 128, 185, 120), width=1)

output_preview_path = os.path.join(art_dir, 'all_characters_option_b_showcase.png')
card.save(output_preview_path)
print(f"Showcase image saved to {output_preview_path}")

# --- 3. Generate Animated Chopping GIF at 140px Scale ---
gif_w, gif_h = 420, 580
frames = []

raw_body = Image.open('public/images/amirhossein_body.png').convert('RGBA').resize((68, 140), Image.Resampling.LANCZOS)
raw_swing = Image.open('public/images/amirhossein_swing.png').convert('RGBA').resize((115, 140), Image.Resampling.LANCZOS)

ground_y = 500
trunk_x = 220

for step in range(12):
    f_img = Image.new('RGBA', (gif_w, gif_h), (24, 40, 72, 255))
    f_draw = ImageDraw.Draw(f_img)

    # Gradient Sky
    for y in range(ground_y):
        ratio = y / ground_y
        r = int(24 + (130 - 24) * ratio)
        g = int(45 + (185 - 45) * ratio)
        b = int(75 + (165 - 75) * ratio)
        f_draw.line([(0, y), (gif_w, y)], fill=(r, g, b, 255))

    # Tree
    f_draw.rectangle([trunk_x, 0, trunk_x + 70, ground_y], fill=(125, 90, 45, 255))

    # Ground
    f_draw.rectangle([0, ground_y, gif_w, gif_h], fill=(115, 168, 70, 255))
    f_draw.line([(0, ground_y), (gif_w, ground_y)], fill=(90, 140, 50, 255), width=3)

    is_swing = (step % 4 in [1, 2])
    
    if is_swing:
        # Swing sprite (115x140)
        sx = trunk_x - 115 + 18
        sy = ground_y - 140
        f_img.paste(raw_swing, (sx, sy), raw_swing)
        # Wood chips flying
        f_draw.rectangle([trunk_x + 35, sy + 50, trunk_x + 50, sy + 60], fill=(195, 145, 85, 255))
        f_draw.rectangle([trunk_x + 70, sy + 25, trunk_x + 85, sy + 35], fill=(195, 145, 85, 255))
        # Blue electric 2X sparks
        f_draw.line([(trunk_x + 20, sy + 40), (trunk_x + 60, sy + 30)], fill=(33, 150, 243, 255), width=2)
    else:
        # Idle sprite (68x140)
        sx = trunk_x - 68 - 8
        sy = ground_y - 140
        f_img.paste(raw_body, (sx, sy), raw_body)

    # Top HUD
    f_draw.rounded_rectangle([15, 15, 210, 65], radius=10, fill=(13, 20, 32, 230), outline=(41, 128, 185, 240), width=2)
    f_draw.text((25, 22), "amirhossein (140px Scale)", font=font_label, fill=(255, 255, 255, 255))
    f_draw.text((25, 42), "⚡ ۲X امتیاز فعال", font=font_badge, fill=(255, 215, 0, 255))

    frames.append(f_img)

gif_path = os.path.join(art_dir, 'option_b_scaled_chopping.gif')
frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=110, loop=0)
print(f"Chopping GIF saved to {gif_path}")
