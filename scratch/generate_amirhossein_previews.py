import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'
body = Image.open('public/images/amirhossein_body.png')
swing = Image.open('public/images/amirhossein_swing.png')
died = Image.open('public/images/amirhossein_died.png')

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 15)
font_body = ImageFont.truetype(font_path, 12)
font_small = ImageFont.truetype(font_path, 10)
font_tiny = ImageFont.truetype(font_path, 9)
font_popup = ImageFont.truetype(font_path, 18)
font_score = ImageFont.truetype(font_path, 22)
font_score_lbl = ImageFont.truetype(font_path, 10)

w, h = 420, 680

# 1. Action Preview Image
scene = Image.new('RGBA', (w, h), (142, 197, 173, 255))
draw = ImageDraw.Draw(scene)

# Sky background
for y in range(h):
    ratio = y / h
    r = int(24 + (142 - 24) * ratio)
    g = int(40 + (197 - 40) * ratio)
    b = int(72 + (173 - 72) * ratio)
    draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

# Tree Trunk in middle
tx1, tx2 = 175, 245
draw.rectangle([tx1, 0, tx2, 560], fill=(130, 95, 49, 255))
for ty in range(20, 560, 45):
    draw.line([(tx1 + 10, ty), (tx1 + 55, ty)], fill=(100, 70, 30, 255), width=3)
    draw.line([(tx1 + 25, ty + 20), (tx1 + 45, ty + 20)], fill=(100, 70, 30, 255), width=2)

# Ground grass
draw.rectangle([0, 550, w, h], fill=(133, 184, 82, 255))
draw.line([(0, 550), (w, 550)], fill=(110, 160, 65, 255), width=3)

# Amirhossein swinging axe on left side
sw_pos = (tx1 - swing.width + 30, 550 - swing.height + 25)
scene.paste(swing, sw_pos, swing)

# Flying wood chips & 2X lightning energy streaks
for cx, cy in [(tx1 + 35, 400), (tx1 + 75, 360), (tx1 + 100, 320), (tx1 + 20, 440)]:
    draw.rectangle([cx, cy, cx + 16, cy + 10], fill=(195, 145, 85, 255))
    draw.line([(cx - 10, cy + 6), (cx - 25, cy + 15)], fill=(33, 150, 243, 240), width=2)
    draw.line([(cx + 10, cy), (cx + 30, cy - 10)], fill=(100, 181, 246, 240), width=3)

# Energy arcs around axe strike
draw.arc([tx1 - 50, 350, tx1 + 40, 450], start=200, end=340, fill=(33, 150, 243, 230), width=3)
draw.arc([tx1 - 40, 360, tx1 + 50, 460], start=210, end=350, fill=(255, 213, 79, 200), width=2)

# Top HUD: Amirhossein Double Points Mode
hud_x, hud_y, hud_w, hud_h = 16, 22, 185, 80
draw.rounded_rectangle([hud_x, hud_y, hud_x + hud_w, hud_y + hud_h], radius=14, fill=(13, 27, 42, 240), outline=(41, 128, 185, 255), width=2)
draw.text((hud_x + 12, hud_y + 8), 'amirhossein', font=font_title, fill=(255, 255, 255, 255))
draw.text((hud_x + 12, hud_y + 32), 'DOUBLE POINTS', font=font_small, fill=(112, 161, 255, 255))
draw.text((hud_x + hud_w - 68, hud_y + 32), '2X ACTIVE', font=font_small, fill=(41, 128, 185, 255))
# Continuous 100% full blue aura energy bar
draw.rounded_rectangle([hud_x + 12, hud_y + 54, hud_x + hud_w - 12, hud_y + 66], radius=6, fill=(0, 0, 0, 180))
draw.rounded_rectangle([hud_x + 12, hud_y + 54, hud_x + hud_w - 12, hud_y + 66], radius=6, fill=(41, 128, 185, 255))

# Top Right: Score counter showing Double Points (+2 per cut)
draw.rounded_rectangle([w - 125, 22, w - 16, 78], radius=12, fill=(18, 28, 44, 220), outline=(245, 176, 65, 200), width=2)
draw.text((w - 110, 28), 'SCORE', font=font_score_lbl, fill=(200, 200, 200, 255))
draw.text((w - 110, 44), '48', font=font_score, fill=(255, 213, 79, 255))
draw.text((w - 65, 48), '(+2)', font=font_body, fill=(100, 181, 246, 255))

# Combat Popup in center
pop_x, pop_y = 50, 190
draw.rounded_rectangle([pop_x, pop_y, pop_x + 320, pop_y + 54], radius=14, fill=(13, 27, 42, 245), outline=(41, 128, 185, 255), width=2)
draw.text((pop_x + 18, pop_y + 16), '⚡ 2X POINTS! +2 SCORE ⚡', font=font_popup, fill=(255, 235, 59, 255))

# 4-Character Selection Bar at Bottom
bar_x, bar_y, bar_w, bar_h = 15, 605, 390, 56
draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=18, fill=(14, 20, 32, 235), outline=(228, 176, 114, 120), width=1)

tabs = [
    ('nima', 'JAVANI', False),
    ('fargol', 'SULTAN', False),
    ('ali', 'FLURRY', False),
    ('amirhossein', '2X POINTS', True)
]
tab_w = bar_w // 4
for i, (name, badge, is_active) in enumerate(tabs):
    tx = bar_x + i * tab_w + 3
    ty = bar_y + 5
    tw = tab_w - 6
    th = bar_h - 10
    if is_active:
        draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=12, fill=(30, 70, 120, 220), outline=(41, 128, 185, 255), width=2)
    t_name_y = ty + 8
    t_badge_y = ty + 24
    draw.text((tx + 6, t_name_y), name[:6] if len(name) > 6 else name, font=font_small, fill=(255, 255, 255, 255))
    badge_col = (112, 161, 255, 255) if is_active else (228, 176, 114, 255)
    draw.text((tx + 6, t_badge_y), badge, font=font_tiny, fill=badge_col)

scene.save(os.path.join(art_dir, 'amirhossein_ingame_action_preview.png'))
print('Saved amirhossein_ingame_action_preview.png')

# 2. Animated GIF: Woodchopping Action with Double Points (+2 per cut)
frames = []
scores = [20, 22, 24, 26, 28]

for cycle in range(3):
    score = scores[cycle]
    
    # Frame 1: Standing ready
    f1 = Image.new('RGBA', (w, h), (142, 197, 173, 255))
    d1 = ImageDraw.Draw(f1)
    for y in range(h):
        ratio = y / h
        r = int(24 + (142 - 24) * ratio)
        g = int(40 + (197 - 40) * ratio)
        b = int(72 + (173 - 72) * ratio)
        d1.line([(0, y), (w, y)], fill=(r, g, b, 255))
    d1.rectangle([tx1, 0, tx2, 560], fill=(130, 95, 49, 255))
    d1.rectangle([0, 550, w, h], fill=(133, 184, 82, 255))
    st_pos = (tx1 - body.width + 10, 550 - body.height + 25)
    f1.paste(body, st_pos, body)

    # HUD
    d1.rounded_rectangle([hud_x, hud_y, hud_x + hud_w, hud_y + hud_h], radius=14, fill=(13, 27, 42, 240), outline=(41, 128, 185, 255), width=2)
    d1.text((hud_x + 12, hud_y + 8), 'amirhossein', font=font_title, fill=(255, 255, 255, 255))
    d1.text((hud_x + 12, hud_y + 32), 'DOUBLE POINTS', font=font_small, fill=(112, 161, 255, 255))
    d1.text((hud_x + hud_w - 68, hud_y + 32), '2X ACTIVE', font=font_small, fill=(41, 128, 185, 255))
    d1.rounded_rectangle([hud_x + 12, hud_y + 54, hud_x + hud_w - 12, hud_y + 66], radius=6, fill=(41, 128, 185, 255))

    # Score
    d1.rounded_rectangle([w - 125, 22, w - 16, 78], radius=12, fill=(18, 28, 44, 220), outline=(245, 176, 65, 200), width=2)
    d1.text((w - 110, 28), 'SCORE', font=font_score_lbl, fill=(200, 200, 200, 255))
    d1.text((w - 110, 44), str(score), font=font_score, fill=(255, 213, 79, 255))

    frames.append(f1)

    # Frame 2: Axe Swing Strike! (+2 Double Points)
    f2 = Image.new('RGBA', (w, h), (142, 197, 173, 255))
    d2 = ImageDraw.Draw(f2)
    for y in range(h):
        ratio = y / h
        r = int(24 + (142 - 24) * ratio)
        g = int(40 + (197 - 40) * ratio)
        b = int(72 + (173 - 72) * ratio)
        d2.line([(0, y), (w, y)], fill=(r, g, b, 255))
    d2.rectangle([tx1, 0, tx2, 560], fill=(130, 95, 49, 255))
    d2.rectangle([0, 550, w, h], fill=(133, 184, 82, 255))
    f2.paste(swing, sw_pos, swing)

    # Flying chips
    d2.rectangle([tx1 + 35, 410, tx1 + 50, 422], fill=(195, 145, 85, 255))
    d2.line([(tx1 + 10, 400), (tx1 + 45, 420)], fill=(33, 150, 243, 255), width=3)
    d2.arc([tx1 - 50, 360, tx1 + 40, 450], start=200, end=340, fill=(33, 150, 243, 230), width=3)

    # HUD
    d2.rounded_rectangle([hud_x, hud_y, hud_x + hud_w, hud_y + hud_h], radius=14, fill=(13, 27, 42, 240), outline=(41, 128, 185, 255), width=2)
    d2.text((hud_x + 12, hud_y + 8), 'amirhossein', font=font_title, fill=(255, 255, 255, 255))
    d2.text((hud_x + 12, hud_y + 32), 'DOUBLE POINTS', font=font_small, fill=(112, 161, 255, 255))
    d2.text((hud_x + hud_w - 68, hud_y + 32), '2X ACTIVE', font=font_small, fill=(41, 128, 185, 255))
    d2.rounded_rectangle([hud_x + 12, hud_y + 54, hud_x + hud_w - 12, hud_y + 66], radius=6, fill=(41, 128, 185, 255))

    # Popup
    d2.rounded_rectangle([pop_x, pop_y, pop_x + 320, pop_y + 54], radius=14, fill=(13, 27, 42, 245), outline=(41, 128, 185, 255), width=2)
    d2.text((pop_x + 18, pop_y + 16), '⚡ 2X POINTS! +2 SCORE ⚡', font=font_popup, fill=(255, 235, 59, 255))

    # Score jumps +2
    d2.rounded_rectangle([w - 125, 22, w - 16, 78], radius=12, fill=(18, 28, 44, 220), outline=(245, 176, 65, 200), width=2)
    d2.text((w - 110, 28), 'SCORE', font=font_score_lbl, fill=(200, 200, 200, 255))
    d2.text((w - 110, 44), str(score + 2), font=font_score, fill=(255, 213, 79, 255))
    d2.text((w - 65, 48), '(+2)', font=font_body, fill=(100, 181, 246, 255))

    frames.append(f2)

    # Frame 3: Impact settling
    f3 = Image.new('RGBA', (w, h), (142, 197, 173, 255))
    d3 = ImageDraw.Draw(f3)
    for y in range(h):
        ratio = y / h
        r = int(24 + (142 - 24) * ratio)
        g = int(40 + (197 - 40) * ratio)
        b = int(72 + (173 - 72) * ratio)
        d3.line([(0, y), (w, y)], fill=(r, g, b, 255))
    d3.rectangle([tx1, 0, tx2, 560], fill=(130, 95, 49, 255))
    d3.rectangle([0, 550, w, h], fill=(133, 184, 82, 255))
    f3.paste(body, st_pos, body)

    # HUD
    d3.rounded_rectangle([hud_x, hud_y, hud_x + hud_w, hud_y + hud_h], radius=14, fill=(13, 27, 42, 240), outline=(41, 128, 185, 255), width=2)
    d3.text((hud_x + 12, hud_y + 8), 'amirhossein', font=font_title, fill=(255, 255, 255, 255))
    d3.text((hud_x + 12, hud_y + 32), 'DOUBLE POINTS', font=font_small, fill=(112, 161, 255, 255))
    d3.text((hud_x + hud_w - 68, hud_y + 32), '2X ACTIVE', font=font_small, fill=(41, 128, 185, 255))
    d3.rounded_rectangle([hud_x + 12, hud_y + 54, hud_x + hud_w - 12, hud_y + 66], radius=6, fill=(41, 128, 185, 255))

    # Score
    d3.rounded_rectangle([w - 125, 22, w - 16, 78], radius=12, fill=(18, 28, 44, 220), outline=(245, 176, 65, 200), width=2)
    d3.text((w - 110, 28), 'SCORE', font=font_score_lbl, fill=(200, 200, 200, 255))
    d3.text((w - 110, 44), str(score + 2), font=font_score, fill=(255, 213, 79, 255))

    frames.append(f3)

frames[0].save(
    os.path.join(art_dir, 'amirhossein_swing_action.gif'),
    save_all=True,
    append_images=frames[1:],
    duration=200,
    loop=0
)
print('Saved amirhossein_swing_action.gif')
