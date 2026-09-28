import os
import re
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'

# --- 1. Code Validation ---
with open('public/js/main.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    html_code = f.read()

with open('src/characters/index.ts', 'r', encoding='utf-8') as f:
    ts_index_code = f.read()

checks = [
    ('Parsa state vars', 'parsaSleepCount' in js_code and 'parsaSleeping' in js_code),
    ('Parsa texture vars', 'tex_parsa_body' in js_code and 'tex_parsa_sleep' in js_code),
    ('Parsa button in index.html', 'btn_select_parsa' in html_code and 'data-char="parsa"' in html_code),
    ('Parsa TypeScript export', 'parsaCharacter' in ts_index_code),
    ('Stamina exhaustion intercept', 'selectedCharacter==="parsa"&&parsaSleepCount<2?triggerParsaNap():Va()' in js_code),
    ('triggerParsaNap function', 'function triggerParsaNap()' in js_code),
    ('Parsa swing in mb()', "selectedCharacter === 'parsa'" in js_code and 'tex_parsa_swing' in js_code),
    ('Parsa died texture in Va()', 'selectedCharacter === \'parsa\' ? tex_parsa_died' in js_code),
    ('Parsa Option B scale (94x140)', 'sa.width = 94' in js_code and 'sa.height = 140' in js_code),
    ('Branch clearance (+40px)', '-pa-40' in js_code),
]

all_passed = True
print("--- Parsa Code Validation ---")
for name, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if not passed:
        all_passed = False

if not all_passed:
    raise RuntimeError("Verification failed: Not all Parsa checks passed!")

print("All Parsa code checks passed successfully!\n")

# --- 2. Generate 5-Character In-Game Comparison Showcase ---
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 16)
font_label = ImageFont.truetype(font_path, 12)
font_badge = ImageFont.truetype(font_path, 11)

chars = [
    ('Nima (Old)', 'public/images/nima_body_old.png', 68, 140, '⚡ جوانی', '#f39c12'),
    ('Fargol (Sultan)', 'public/images/fargol_body.png', 86, 140, '🔥 سلطان', '#e74c3c'),
    ('Ali (Architect)', 'public/images/ali_body.png', 68, 140, '🪓 رگبار ۱۰', '#e67e22'),
    ('Amirhossein', 'public/images/amirhossein_body.png', 68, 140, '⚡ ۲X امتیاز', '#3498db'),
    ('Parsa (Chubby)', 'public/images/parsa_body.png', 94, 140, '💤 ۲ پتو', '#9b59b6'),
]

w, h = 1100, 480
card = Image.new('RGBA', (w, h), (18, 26, 42, 255))
draw = ImageDraw.Draw(card)

# Title Header
draw.rectangle([0, 0, w, 60], fill=(13, 20, 32, 255))
draw.line([(0, 60), (w, 60)], fill=(155, 89, 182, 200), width=2)
draw.text((25, 18), "Khanqah Rush - All 5 Playable Characters (Heroic Scale & Elevated Branch Clearance)", font=font_title, fill=(255, 215, 0, 255))

panel_w = w // 5

for i, (name, img_path, spr_w, spr_h, badge, col) in enumerate(chars):
    px = i * panel_w
    # Sky backdrop
    for y in range(61, 410):
        ratio = (y - 61) / (410 - 61)
        r = int(24 + (130 - 24) * ratio)
        g = int(45 + (180 - 45) * ratio)
        b = int(75 + (160 - 75) * ratio)
        draw.line([(px, y), (px + panel_w, y)], fill=(r, g, b, 255))

    # Tree trunk
    tx1 = px + panel_w - 60
    tx2 = tx1 + 50
    draw.rectangle([tx1, 61, tx2, 410], fill=(125, 90, 45, 255))
    for ty in range(80, 410, 40):
        draw.line([(tx1 + 5, ty), (tx1 + 45, ty)], fill=(95, 65, 28, 255), width=2)

    # Elevated branch (+40px clearance above head)
    bx1 = tx1 - 55
    by = 225  # elevated
    draw.rectangle([bx1, by, tx1, by + 22], fill=(105, 75, 38, 255))
    draw.rectangle([bx1, by + 16, tx1, by + 22], fill=(70, 50, 25, 255))
    # Green foliage on branch
    draw.ellipse([bx1 - 10, by - 12, bx1 + 35, by + 30], fill=(60, 140, 50, 255))

    # Ground line
    draw.rectangle([px, 410, px + panel_w, h], fill=(115, 168, 70, 255))
    draw.line([(px, 410), (px + panel_w, 410)], fill=(90, 140, 50, 255), width=3)

    # Load character sprite
    spr = Image.open(img_path).convert('RGBA')
    scaled = spr.resize((spr_w, spr_h), Image.Resampling.LANCZOS)
    cx = px + (panel_w - spr_w) // 2 - 15
    cy = 410 - spr_h
    card.paste(scaled, (cx, cy), scaled)

    # Label box
    draw.rounded_rectangle([px + 10, 70, px + panel_w - 10, 115], radius=6, fill=(10, 15, 25, 220), outline=col, width=1)
    draw.text((px + 16, 75), name, font=font_label, fill=(255, 255, 255, 255))
    draw.text((px + 16, 95), f"{spr_w}x{spr_h}px | {badge}", font=font_badge, fill=col)

    # Headroom clearance indicator
    head_y = cy
    clearance = by + 22
    draw.line([(cx + spr_w // 2, clearance), (cx + spr_w // 2, head_y)], fill=(46, 204, 113, 255), width=2)
    gap = head_y - clearance
    draw.text((cx + spr_w // 2 + 5, (clearance + head_y) // 2 - 6), f"+{gap}px gap", font=font_badge, fill=(46, 204, 113, 255))

    # Divider line
    if i < 4:
        draw.line([(px + panel_w, 61), (px + panel_w, h)], fill=(40, 50, 70, 255), width=2)

card.save(os.path.join(art_dir, 'all_5_characters_showcase.png'))
print('Saved all_5_characters_showcase.png successfully!')

# --- 3. Generate Parsa In-Game Action Showcase (Standing, Chopping, Sleeping Blanket, Defeat) ---
pw, ph = 880, 480
parsa_card = Image.new('RGBA', (pw, ph), (18, 26, 42, 255))
p_draw = ImageDraw.Draw(parsa_card)

# Header
p_draw.rectangle([0, 0, pw, 60], fill=(13, 20, 32, 255))
p_draw.line([(0, 60), (pw, 60)], fill=(155, 89, 182, 200), width=2)
p_draw.text((25, 18), "Parsa (پارسا) - Gameplay States (Standing, Chopping, Blanket Nap & Defeat)", font=font_title, fill=(241, 196, 15, 255))

states = [
    ('1. Standing (Idle)', 'public/images/parsa_body.png', 94, 140, 'Ready to Chop', '#9b59b6'),
    ('2. Woodchopping Swing', 'public/images/parsa_swing.png', 120, 140, 'Axe Impact', '#e67e22'),
    ('3. Blanket Nap (2x Max)', 'public/images/parsa_sleep.png', 94, 140, '🛌 Stamina Refill! 💤', '#f1c40f'),
    ('4. Slumped Defeat', 'public/images/parsa_died.png', 95, 111, 'Out of Blankets', '#e74c3c'),
]

st_w = pw // 4

for i, (name, img_path, spr_w, spr_h, sub, col) in enumerate(states):
    px = i * st_w
    # Sky backdrop
    for y in range(61, 410):
        ratio = (y - 61) / (410 - 61)
        r = int(24 + (130 - 24) * ratio)
        g = int(45 + (180 - 45) * ratio)
        b = int(75 + (160 - 75) * ratio)
        p_draw.line([(px, y), (px + st_w, y)], fill=(r, g, b, 255))

    # Tree trunk
    tx1 = px + st_w - 60
    tx2 = tx1 + 50
    p_draw.rectangle([tx1, 61, tx2, 410], fill=(125, 90, 45, 255))

    # Ground
    p_draw.rectangle([px, 410, px + st_w, ph], fill=(115, 168, 70, 255))
    p_draw.line([(px, 410), (px + st_w, 410)], fill=(90, 140, 50, 255), width=3)

    # Character sprite
    spr = Image.open(img_path).convert('RGBA')
    scaled = spr.resize((spr_w, spr_h), Image.Resampling.LANCZOS)
    cx = px + (st_w - spr_w) // 2 - (15 if i != 1 else 0)
    cy = 410 - spr_h
    parsa_card.paste(scaled, (cx, cy), scaled)

    # State label card
    p_draw.rounded_rectangle([px + 10, 70, px + st_w - 10, 120], radius=6, fill=(10, 15, 25, 220), outline=col, width=1)
    p_draw.text((px + 16, 76), name, font=font_label, fill=(255, 255, 255, 255))
    p_draw.text((px + 16, 98), sub, font=font_badge, fill=col)

    # Divider
    if i < 3:
        p_draw.line([(px + st_w, 61), (px + st_w, ph)], fill=(40, 50, 70, 255), width=2)

parsa_card.save(os.path.join(art_dir, 'parsa_ingame_action_preview.png'))
print('Saved parsa_ingame_action_preview.png successfully!')

# --- 4. Animated GIF: Parsa Chopping & Blanket Power Nap ---
frames = []
bg_sim = Image.new('RGBA', (320, 360), (28, 36, 52, 255))
bg_draw = ImageDraw.Draw(bg_sim)
for y in range(0, 310):
    ratio = y / 310
    bg_draw.line([(0, y), (320, y)], fill=(int(24 + 100*ratio), int(45 + 130*ratio), int(75 + 80*ratio), 255))
# Tree trunk
bg_draw.rectangle([210, 0, 260, 310], fill=(125, 90, 45, 255))
# Ground
bg_draw.rectangle([0, 310, 320, 360], fill=(115, 168, 70, 255))

body_spr = Image.open('public/images/parsa_body.png').resize((94, 140), Image.Resampling.LANCZOS)
swing_spr = Image.open('public/images/parsa_swing.png').resize((120, 140), Image.Resampling.LANCZOS)
sleep_spr = Image.open('public/images/parsa_sleep.png').resize((94, 140), Image.Resampling.LANCZOS)

# 1. Idle frame (2 frames)
f1 = bg_sim.copy()
f1.paste(body_spr, (110, 310 - 140), body_spr)
d1 = ImageDraw.Draw(f1)
d1.rectangle([10, 10, 110, 36], fill=(10, 15, 25, 200), outline=(155, 89, 182, 255))
d1.text((16, 14), "Parsa: 2/2 Blankets", font=font_badge, fill=(241, 196, 15, 255))
frames.extend([f1] * 3)

# 2. Swing chop frame (3 chops)
for ch in range(3):
    f_sw = bg_sim.copy()
    f_sw.paste(swing_spr, (120, 310 - 140), swing_spr)
    d = ImageDraw.Draw(f_sw)
    d.rectangle([10, 10, 110, 36], fill=(10, 15, 25, 200), outline=(155, 89, 182, 255))
    d.text((16, 14), f"Chop +1 (Score: {ch+1})", font=font_badge, fill=(255, 255, 255, 255))
    frames.append(f_sw)
    
    f_id = bg_sim.copy()
    f_id.paste(body_spr, (120, 310 - 140), body_spr)
    d_i = ImageDraw.Draw(f_id)
    d_i.rectangle([10, 10, 110, 36], fill=(10, 15, 25, 200), outline=(155, 89, 182, 255))
    d_i.text((16, 14), f"Chop +1 (Score: {ch+1})", font=font_badge, fill=(255, 255, 255, 255))
    frames.append(f_id)

# 3. Stamina Exhaustion -> Blanket Nap
for z in range(6):
    f_sl = bg_sim.copy()
    f_sl.paste(sleep_spr, (120, 310 - 140), sleep_spr)
    d_sl = ImageDraw.Draw(f_sl)
    d_sl.rectangle([10, 10, 150, 36], fill=(45, 20, 60, 220), outline=(241, 196, 15, 255))
    d_sl.text((16, 14), "🛌 BLANKET NAP! 100% 💤", font=font_badge, fill=(241, 196, 15, 255))
    frames.append(f_sl)

# 4. Wakes up refreshed with 1 blanket left
f_wake = bg_sim.copy()
f_wake.paste(body_spr, (120, 310 - 140), body_spr)
d_w = ImageDraw.Draw(f_wake)
d_w.rectangle([10, 10, 130, 36], fill=(10, 15, 25, 200), outline=(155, 89, 182, 255))
d_w.text((16, 14), "Refreshed! 1/2 Left", font=font_badge, fill=(46, 204, 113, 255))
frames.extend([f_wake] * 4)

gif_path = os.path.join(art_dir, 'parsa_nap_and_chop.gif')
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=180,
    loop=0
)
print('Saved parsa_nap_and_chop.gif successfully!')
