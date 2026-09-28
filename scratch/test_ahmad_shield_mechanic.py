import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'

# 1. Code Invariant Checks
with open('public/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('src/characters/index.ts', 'r', encoding='utf-8') as f:
    chars_idx = f.read()

checks = [
    ('ahmadChops state in JS', 'var ahmadChops = 0;' in js),
    ('ahmadShieldActive state in JS', 'var ahmadShieldActive = false;' in js),
    ('tex_ahmad_body texture', 'tex_ahmad_body' in js),
    ('tex_ahmad_swing texture', 'tex_ahmad_swing' in js),
    ('tex_ahmad_died texture', 'tex_ahmad_died' in js),
    ('btn_select_ahmad in index.html', 'id="btn_select_ahmad"' in html),
    ('btn_select_ahmad in JS init', 'btn_select_ahmad' in js),
    ('100-Chop Shield activation in Ca(a)', 'ahmadChops % 100 === 0' in js and 'ahmadShieldActive = true;' in js),
    ('Branch collision absorption in Ca(a)', 'selectedCharacter === \'ahmad\' && ahmadShieldActive' in js and '1 == Math.abs(b_ahm) && $a(a, !0);' in js),
    ('Lethal event interception in Va()', 'selectedCharacter === \'ahmad\' && ahmadShieldActive' in js and 'سپر از احمد محافظت کرد' in js),
    ('Ahmad character in index.ts', 'ahmadCharacter' in chars_idx),
    ('Ahmad sprites exist in public/images', (
        os.path.exists('public/images/ahmad_body.png') and
        os.path.exists('public/images/ahmad_swing.png') and
        os.path.exists('public/images/ahmad_died.png')
    ))
]

print("=== Ahmad Shield Mechanic & Assets Code Invariants ===")
all_passed = True
for name, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if not passed:
        all_passed = False

if not all_passed:
    raise RuntimeError("Verification failed on Ahmad invariants!")

print("\nAll 12 code invariants passed successfully!\n")

# 2. Generate Animated GIF: Ahmad 100 Chops -> Shield Activation -> Lethal Branch Hit Absorption
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_badge = ImageFont.truetype(font_path, 11)
font_title = ImageFont.truetype(font_path, 13)
font_popup = ImageFont.truetype(font_path, 12)

frames = []
canvas_w, canvas_h = 360, 380

bg_base = Image.new('RGBA', (canvas_w, canvas_h), (20, 28, 40, 255))
d_base = ImageDraw.Draw(bg_base)
for y in range(0, 320):
    r_val = int(18 + 70 * (y / 320))
    g_val = int(32 + 90 * (y / 320))
    b_val = int(55 + 60 * (y / 320))
    d_base.line([(0, y), (canvas_w, y)], fill=(r_val, g_val, b_val, 255))

# Tree trunk
d_base.rectangle([240, 0, 290, 320], fill=(125, 90, 45, 255))
# Tree bark detail
for ty in range(20, 320, 40):
    d_base.line([(248, ty), (252, ty + 25)], fill=(90, 60, 30, 255), width=2)
    d_base.line([(275, ty + 10), (278, ty + 30)], fill=(90, 60, 30, 255), width=2)
# Ground
d_base.rectangle([0, 320, canvas_w, canvas_h], fill=(115, 168, 70, 255))

body_spr = Image.open('public/images/ahmad_body.png').resize((94, 140), Image.Resampling.LANCZOS)
swing_spr = Image.open('public/images/ahmad_swing.png').resize((120, 140), Image.Resampling.LANCZOS)

char_x = 135
char_y = 320 - 140

def draw_hud(frame, progress_pct, progress_text, shield_active):
    d = ImageDraw.Draw(frame)
    # HUD Box
    outline_col = (241, 196, 15, 255) if shield_active else (52, 152, 219, 200)
    bg_col = (20, 35, 55, 230) if shield_active else (15, 22, 32, 210)
    d.rounded_rectangle([10, 10, 200, 56], radius=7, fill=bg_col, outline=outline_col, width=2 if shield_active else 1)
    
    # Title & Badge
    title = "🛡️ ahmad (سپر فعال)" if shield_active else "🛡️ ahmad"
    d.text((16, 14), title, font=font_badge, fill=(241, 196, 15, 255) if shield_active else (255, 255, 255, 255))
    d.text((135, 14), progress_text, font=font_badge, fill=(241, 196, 15, 255) if shield_active else (93, 173, 226, 255))
    
    # Progress Track
    d.rectangle([16, 36, 194, 46], fill=(0, 0, 0, 180))
    fill_w = int(178 * (progress_pct / 100))
    if fill_w > 0:
        fill_col = (241, 196, 15, 255) if shield_active else (52, 152, 219, 255)
        d.rectangle([16, 36, 16 + fill_w, 46], fill=fill_col)

def draw_shield_barrier(frame, alpha=140):
    barrier = Image.new('RGBA', frame.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(barrier)
    # Glowing protective oval barrier
    bd.ellipse([char_x - 14, char_y - 8, char_x + 108, char_y + 144], 
               fill=(52, 152, 219, int(alpha * 0.25)), 
               outline=(241, 196, 15, alpha), width=3)
    # Cross crest on barrier
    cx, cy = char_x + 47, char_y + 65
    bd.line([(cx - 18, cy), (cx + 18, cy)], fill=(241, 196, 15, int(alpha * 0.9)), width=2)
    bd.line([(cx, cy - 22), (cx, cy + 22)], fill=(241, 196, 15, int(alpha * 0.9)), width=2)
    return Image.alpha_composite(frame, barrier)

# Step 1: Chopping sequence approaching 100 chops (e.g. 96 to 99)
for chop_num in [96, 97, 98, 99]:
    # Swing frame
    f_sw = bg_base.copy()
    f_sw.paste(swing_spr, (char_x - 12, char_y), swing_spr)
    draw_hud(f_sw, chop_num, f"{chop_num}/100", False)
    frames.append(f_sw)
    
    # Return to body frame
    f_bd = bg_base.copy()
    f_bd.paste(body_spr, (char_x, char_y), body_spr)
    draw_hud(f_bd, chop_num, f"{chop_num}/100", False)
    frames.append(f_bd)

# Step 2: The 100th Chop! Hits 100/100 -> Shield Activates!
f_100_sw = bg_base.copy()
f_100_sw.paste(swing_spr, (char_x - 12, char_y), swing_spr)
draw_hud(f_100_sw, 100, "100/100", False)
frames.append(f_100_sw)

# Golden Shield Activation Popup
for pulse in range(6):
    f_active = bg_base.copy()
    f_active.paste(body_spr, (char_x, char_y), body_spr)
    f_active = draw_shield_barrier(f_active, alpha=160 + (pulse % 2) * 50)
    draw_hud(f_active, 100, "🛡️ سپر فعال", True)
    d = ImageDraw.Draw(f_active)
    # Combat popup
    d.rounded_rectangle([60, 95, 300, 130], radius=8, fill=(20, 35, 60, 240), outline=(241, 196, 15, 255), width=2)
    d.text((75, 103), "🛡️ سپر احمد فعال شد! 🛡️", font=font_popup, fill=(241, 196, 15, 255))
    frames.append(f_active)

# Step 3: Branch descends! Lethal Branch on Left at y=170
branch_col = (110, 75, 35, 255)
for br_y in [140, 180, 210]:
    f_br = bg_base.copy()
    f_br.paste(body_spr, (char_x, char_y), body_spr)
    f_br = draw_shield_barrier(f_br, alpha=190)
    # Draw descending lethal branch
    d = ImageDraw.Draw(f_br)
    d.rounded_rectangle([190, br_y, 250, br_y + 22], radius=4, fill=branch_col, outline=(70, 45, 20, 255))
    draw_hud(f_br, 100, "🛡️ سپر فعال", True)
    frames.append(f_br)

# Step 4: Branch collides into Shield! Shield shatters the branch & saves Ahmad!
f_impact = bg_base.copy()
f_impact.paste(body_spr, (char_x, char_y), body_spr)
# Shattered shield burst
d_imp = ImageDraw.Draw(f_impact)
cx, cy = char_x + 50, char_y + 60
# Branch debris flying
for offset in [(-30, -20), (20, -35), (-40, 15), (35, 25), (-15, -45)]:
    bx, by = cx + offset[0], cy + offset[1]
    d_imp.rectangle([bx, by, bx + 10, by + 6], fill=(130, 90, 45, 255))
# Shield shard lines
for sx, sy in [(-25, -25), (30, -20), (-20, 30), (25, 25)]:
    d_imp.line([(cx, cy), (cx + sx, cy + sy)], fill=(241, 196, 15, 255), width=3)

d_imp.rounded_rectangle([25, 95, 335, 130], radius=8, fill=(40, 15, 15, 245), outline=(231, 76, 60, 255), width=2)
d_imp.text((36, 103), "🛡️ سپر شکست و جان احمد را نجات داد! 💥", font=font_popup, fill=(241, 196, 15, 255))
draw_hud(f_impact, 0, "0/100", False)
frames.append(f_impact)

# Step 5: Ahmad continues chopping unharmed!
for ch in range(3):
    f_safe = bg_base.copy()
    f_safe.paste(swing_spr if ch % 2 == 0 else body_spr, (char_x - 12 if ch % 2 == 0 else char_x, char_y), swing_spr if ch % 2 == 0 else body_spr)
    draw_hud(f_safe, ch + 1, f"{ch + 1}/100", False)
    frames.append(f_safe)

gif_path = os.path.join(art_dir, 'ahmad_shield_chop_action.gif')
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=260,
    loop=0
)
print(f"Saved {gif_path} successfully!")

# 3. Create All 6 Playable Characters Showcase Image
showcase_w = 780
showcase_h = 290
showcase = Image.new('RGBA', (showcase_w, showcase_h), (18, 22, 32, 255))
s_draw = ImageDraw.Draw(showcase)

# Banner
s_draw.rectangle([0, 0, showcase_w, 48], fill=(28, 36, 52, 255))
s_draw.line([(0, 48), (showcase_w, 48)], fill=(52, 73, 94, 255), width=2)
s_draw.text((22, 14), "KHANQAH RUSH — ALL 6 PLAYABLE HEROES (OPTION B HEROIC SCALE 140PX)", font=font_title, fill=(241, 196, 15, 255))

# Character slot info
char_data = [
    ("nima", "🧔 Nima", "⚡ جوانی", "public/images/nima_body_old.png", 68, 140),
    ("fargol", "👑 Fargol", "🔥 فداکاری", "public/images/fargol_body.png", 86, 140),
    ("ali", "👓 Ali", "🪓 رگبار ۱۰", "public/images/ali_body.png", 68, 140),
    ("amirhossein", "🧢 Amirhossein", "⚡ ۲X امتیاز", "public/images/amirhossein_body.png", 68, 140),
    ("parsa", "🛌 Parsa", "💤 ۲ پتو", "public/images/parsa_body.png", 94, 140),
    ("ahmad", "🛡️ Ahmad", "🛡️ سپر ۱۰۰", "public/images/ahmad_body.png", 94, 140),
]

slot_w = showcase_w // 6
for idx, (cid, name, badge, path, cw, ch) in enumerate(char_data):
    sx = idx * slot_w
    # Slot card background
    is_ahmad = (cid == 'ahmad')
    card_bg = (30, 48, 70, 240) if is_ahmad else (24, 30, 42, 220)
    card_border = (241, 196, 15, 255) if is_ahmad else (44, 62, 80, 255)
    s_draw.rounded_rectangle([sx + 6, 56, sx + slot_w - 6, showcase_h - 10], radius=8, fill=card_bg, outline=card_border, width=2 if is_ahmad else 1)
    
    # Title & Badge
    s_draw.text((sx + 14, 64), name, font=font_badge, fill=(241, 196, 15, 255) if is_ahmad else (255, 255, 255, 255))
    s_draw.text((sx + 14, 80), badge, font=font_badge, fill=(52, 152, 219, 255) if is_ahmad else (189, 195, 199, 255))
    
    # Ground mound in slot
    s_draw.rounded_rectangle([sx + 12, showcase_h - 40, sx + slot_w - 12, showcase_h - 18], radius=6, fill=(115, 168, 70, 255))
    
    # Character Sprite
    if os.path.exists(path):
        c_img = Image.open(path).resize((cw, ch), Image.Resampling.LANCZOS)
        paste_x = sx + (slot_w - cw) // 2
        paste_y = (showcase_h - 22) - ch
        showcase.paste(c_img, (paste_x, paste_y), c_img)

showcase_path = os.path.join(art_dir, 'all_6_characters_showcase.png')
showcase.save(showcase_path)
print(f"Saved {showcase_path} successfully!")
